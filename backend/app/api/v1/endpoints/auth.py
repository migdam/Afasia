"""Authentication endpoints."""
import time

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ....db.database import get_db
from ....db.models import User
from ....core import login_limit
from ....core.config import settings
from ....core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    credentials_error,
    decode_token,
    get_current_user_id,
    security,
)
from ..schemas import UserCreate, UserLogin, TokenResponse, UserResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
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

    return TokenResponse(
        access_token=create_access_token(user.id),
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user."""
    wait = login_limit.retry_after(credentials.username)
    if wait:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please wait and try again.",
            headers={"Retry-After": str(wait)},
        )

    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        login_limit.record_failure(credentials.username)
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

    login_limit.record_success(credentials.username)
    return TokenResponse(
        access_token=create_access_token(user.id),
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    user_id: int = Depends(get_current_user_id),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Swap a valid token for a fresh one, keeping the original login time.

    The frontend calls this while the user is active, so a login only ends
    after ACCESS_TOKEN_EXPIRE_MINUTES of not using the app, or
    LOGIN_MAX_HOURS after logging in, whichever comes first.
    """
    auth_time = decode_token(credentials.credentials).get("auth_time")
    if not isinstance(auth_time, int) or time.time() - auth_time >= settings.LOGIN_MAX_HOURS * 3600:
        raise credentials_error()

    user = db.get(User, user_id)
    return TokenResponse(
        access_token=create_access_token(user.id, auth_time=auth_time),
        user=UserResponse.model_validate(user)
    )
