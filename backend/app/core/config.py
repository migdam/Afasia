"""Application configuration."""
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The README has people copy .env.template to the repository root, where
# docker compose reads the same file, so .env is read from there whatever the
# working directory. ENV_FILE overrides the location (the tests use this).
ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


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
    DEBUG: bool = True

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "sqlite:///./aphasia_app.db"

    # CORS (comma-separated; use cors_origins for the list)
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"

    @property
    def cors_origins(self) -> list[str]:
        """BACKEND_CORS_ORIGINS split on commas, without blanks."""
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
