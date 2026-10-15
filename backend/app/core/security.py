"""Security utilities for authentication and authorization."""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
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


def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> int:
    """Get the current user's ID from the Bearer token.

    The account is looked up on every request, so a token stops working as
    soon as its user is deactivated or deleted.
    """
    if credentials is None:
        raise credentials_error()
    try:
        user_id = int(decode_token(credentials.credentials)["sub"])
    except ValueError:
        raise credentials_error() from None
    active = db.query(User.is_active).filter(User.id == user_id).scalar()
    if not active:
        raise credentials_error()
    return user_id
