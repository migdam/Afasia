"""Database configuration and session management."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


def migrate(bind=None):
    """Bring a database (the app's, by default) to the latest schema with the
    Alembic migrations in backend/migrations (backlog P3-1)."""
    from alembic import command
    from alembic.config import Config

    config = Config(str(ALEMBIC_INI))
    with (bind or engine).begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")


def init_db():
    """Set up the database: run any migrations it hasn't had yet."""
    migrate()
