"""Security utilities for authentication and authorization."""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import User
from .config import settings

# bcrypt only looks at the first 72 bytes of a password. Longer ones are
# refused at sign-up rather than silently cut short.
MAX_PASSWORD_BYTES = 72
# Without auto_error, a missing or non-Bearer Authorization header reaches
# get_current_user_id, which answers 401 (FastAPI's own answer is 403).
security = HTTPBearer(auto_error=False)

# Browsers get the token in an httpOnly cookie, out of reach of page scripts.
# Other clients may still send it as a Bearer header.
COOKIE_NAME = "access_token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash (passlib's hashes included)."""
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except ValueError:  # over 72 bytes, or not a bcrypt hash
        return False


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None,
    auth_time: Optional[int] = None,
) -> str:
    """Create a JWT access token for a user.

    auth_time is when the user actually logged in (Unix time); renewed tokens
    keep it, so a login can't be stretched past LOGIN_MAX_HOURS.
    """
    now = datetime.now(timezone.utc)
    issued = int(now.timestamp())
    auth_time = issued if auth_time is None else auth_time
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    latest = datetime.fromtimestamp(auth_time + settings.LOGIN_MAX_HOURS * 3600, timezone.utc)
    # A JWT subject must be a string (RFC 7519, section 4.1.2).
    claims = {"sub": str(user_id), "iat": issued, "auth_time": auth_time, "exp": min(expire, latest)}
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def credentials_error() -> HTTPException:
    """The 401 for a missing or invalid token."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_token(token: str) -> dict:
    """Decode and verify a JWT access token."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        raise credentials_error() from None


def set_login_cookie(response: Response, token: str) -> None:
    """Hand the browser its login as an httpOnly cookie that ends with the token."""
    max_age = decode_token(token)["exp"] - int(datetime.now(timezone.utc).timestamp())
    response.set_cookie(
        COOKIE_NAME, token, max_age=max(max_age, 0), path="/api",
        httponly=True, secure=settings.COOKIE_SECURE, samesite="strict",
    )


def clear_login_cookie(response: Response) -> None:
    response.delete_cookie(
        COOKIE_NAME, path="/api", httponly=True, secure=settings.COOKIE_SECURE, samesite="strict",
    )


def get_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """The request's token, from the Bearer header or else the login cookie.

    A browser sends the cookie even on requests another site starts, so a
    change made through the cookie must carry an X-Requested-With header:
    a cross-site page can only add one after a CORS check, and CORS allows
    only our own origins.
    """
    if credentials is not None:
        return credentials.credentials
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise credentials_error()
    if request.method not in SAFE_METHODS and not request.headers.get("X-Requested-With"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing X-Requested-With header")
    return token


def get_current_user_id(
    token: str = Depends(get_token),
    db: Session = Depends(get_db),
) -> int:
    """Get the current user's ID from the token.

    The account is looked up on every request, so a token stops working as
    soon as its user is deactivated or deleted.
    """
    try:
        user_id = int(decode_token(token)["sub"])
    except ValueError:
        raise credentials_error() from None
    active = db.query(User.is_active).filter(User.id == user_id).scalar()
    if not active:
        raise credentials_error()
    return user_id
