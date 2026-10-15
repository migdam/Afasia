"""Application configuration."""
import os
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The README has people copy .env.template to the repository root, where
# docker compose reads the same file, so .env is read from there whatever the
# working directory. ENV_FILE overrides the location (the tests use this).
ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

# The example key in .env.template: public, so it must never sign tokens.
TEMPLATE_SECRET_KEY = "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=os.environ.get("ENV_FILE", ROOT_ENV_FILE),
        # The root .env is shared with docker compose, so keys the app
        # doesn't use are ignored instead of rejected.
        extra="ignore",
        case_sensitive=True,
    )

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    # Off unless asked for: debug mode shows more in errors and logs.
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    # A login ends after this many minutes without using the app; the
    # frontend renews it while the user is active...
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # ...but never for longer than this after logging in.
    LOGIN_MAX_HOURS: int = 12
    # Send the login cookie over HTTPS only. Browsers make an exception for
    # http://localhost; turn this off only for plain-HTTP testing elsewhere.
    COOKIE_SECURE: bool = True
    # Wrong passwords (app/core/login_limit.py): per username and client
    # address, and per account from any address, within LOGIN_LOCK_MINUTES.
    LOGIN_MAX_FAILURES: int = 5
    LOGIN_MAX_FAILURES_PER_ACCOUNT: int = 50
    LOGIN_LOCK_MINUTES: int = 15

    # Delete recordings older than this many days (app/retention.py);
    # 0 keeps them until the person deletes them or their account.
    RECORDING_RETENTION_DAYS: int = 0

    # Suggesting another level (backlog P2-8c): from the average score of
    # the last LEVEL_WINDOW finished sessions of a type at one level, a
    # harder level from LEVEL_UP_SCORE (%) up, an easier one below
    # LEVEL_DOWN_SCORE. Placeholders, pending clinical review (C3, C7).
    LEVEL_WINDOW: int = 3
    LEVEL_UP_SCORE: float = 85.0
    LEVEL_DOWN_SCORE: float = 50.0

    # Database
    DATABASE_URL: str = "sqlite:///./aphasia_app.db"

    # CORS (comma-separated; use cors_origins for the list)
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_is_safe(cls, key: str) -> str:
        """Refuse keys that let anyone forge logins."""
        how = "Generate one with: openssl rand -hex 32"
        if key == TEMPLATE_SECRET_KEY:
            raise ValueError(f"SECRET_KEY is still the example from .env.template. {how}")
        # HS256 needs at least 32 bytes (RFC 7518, section 3.2).
        if len(key.encode()) < 32:
            raise ValueError(f"SECRET_KEY must be at least 32 bytes. {how}")
        return key

    @property
    def cors_origins(self) -> list[str]:
        """BACKEND_CORS_ORIGINS split on commas, without blanks."""
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
