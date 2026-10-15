"""Security utilities for authentication and authorization."""
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Without auto_error, a missing or non-Bearer Authorization header reaches
# get_current_user_id, which answers 401 (FastAPI's own answer is 403).
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for a user."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # A JWT subject must be a string (RFC 7519, section 4.1.2).
    claims = {"sub": str(user_id), "exp": expire}
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
) -> int:
    """Get the current user's ID from the Bearer token."""
    if credentials is None:
        raise credentials_error()
    try:
        return int(decode_token(credentials.credentials)["sub"])
    except ValueError:
        raise credentials_error() from None
