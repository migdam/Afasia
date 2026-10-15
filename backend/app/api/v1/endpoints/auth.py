"""Authentication endpoints."""
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ....db.database import get_db
from ....db.models import RevokedLogin, User
from ....core import login_limit
from ....core.config import settings
from ....core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    clear_login_cookie,
    credentials_error,
    decode_token,
    get_current_user_id,
    get_token,
    security,
    set_login_cookie,
)
from ..schemas import UserCreate, UserLogin, TokenResponse, UserResponse

router = APIRouter()


def login_response(response: Response, user: User, token: str, show_token: bool = True) -> TokenResponse:
    """Set the login cookie and describe the token (with the token itself if show_token)."""
    set_login_cookie(response, token)
    claims = decode_token(token)
    return TokenResponse(
        access_token=token if show_token else None,
        issued_at=claims["iat"],
        expires_at=claims["exp"],
        user=UserResponse.model_validate(user),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        language=user_data.language,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return login_response(response, user, create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    """Login user."""
    client = request.client.host if request.client else "unknown"
    wait = login_limit.retry_after(credentials.username, client)
    if wait:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please wait and try again.",
            headers={"Retry-After": str(wait)},
        )

    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        login_limit.record_failure(credentials.username, client)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    login_limit.record_success(credentials.username, client)
    return login_response(response, user, create_access_token(user.id))


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    user_id: int = Depends(get_current_user_id),
    token: str = Depends(get_token),
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Swap a valid token for a fresh one, keeping the original login time.

    The frontend calls this while the user is active, so a login only ends
    after ACCESS_TOKEN_EXPIRE_MINUTES of not using the app, or
    LOGIN_MAX_HOURS after logging in, whichever comes first.
    """
    claims = decode_token(token)
    auth_time = claims.get("auth_time")
    if not isinstance(auth_time, int) or time.time() - auth_time >= settings.LOGIN_MAX_HOURS * 3600:
        raise credentials_error()

    user = db.get(User, user_id)
    # Through the cookie, the new token goes only into the cookie: a script
    # on the page could otherwise read it from the body.
    new_token = create_access_token(user.id, auth_time=auth_time, sid=claims["sid"])
    return login_response(response, user, new_token, show_token=bearer is not None)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """End this login: its tokens are refused from now on, and the cookie goes.

    Works without a valid login too (then it only removes the cookie), so
    the app can always log out.
    """
    clear_login_cookie(response)
    try:
        claims = decode_token(get_token(request, bearer))
    except HTTPException:
        return
    now = int(time.time())
    db.query(RevokedLogin).filter(RevokedLogin.expires_at < now).delete()
    if not db.get(RevokedLogin, str(claims["sid"])):
        expires_at = max(claims["exp"], claims.get("auth_time", now) + settings.LOGIN_MAX_HOURS * 3600)
        db.add(RevokedLogin(sid=str(claims["sid"]), expires_at=int(expires_at)))
    db.commit()
