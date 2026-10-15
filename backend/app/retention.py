"""Deleting recordings once they are older than RECORDING_RETENTION_DAYS.

0 (the default) keeps recordings until the person deletes them or their
account. How long they should be kept is a decision for whoever runs the
app (backlog H4). With a limit set, the server cleans up when it starts and
then once a day; `python -m app.cli delete-old-recordings` does it at once.
"""
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from .core.clock import utcnow
from .core.config import settings
from .core.logging import logger
from .db.database import SessionLocal
from .db.models import AudioRecording

CLEAN_UP_EVERY_SECONDS = 24 * 60 * 60


def delete_old_recordings(db: Session, days: int) -> int:
    """Delete recordings made more than `days` days ago, files included.

    Returns how many were deleted.
    """
    cutoff = utcnow() - timedelta(days=days)
    old = db.query(AudioRecording).filter(AudioRecording.created_at < cutoff).all()
    files = [Path(recording.file_path) for recording in old]
    for recording in old:
        db.delete(recording)
    db.commit()
    for path in files:
        path.unlink(missing_ok=True)
    return len(old)


def clean_up_now() -> int:
    with SessionLocal() as db:
        deleted = delete_old_recordings(db, settings.RECORDING_RETENTION_DAYS)
    logger.info("Deleted old recordings", count=deleted, retention_days=settings.RECORDING_RETENTION_DAYS)
    return deleted


async def clean_up() -> None:
    try:
        await asyncio.to_thread(clean_up_now)
    except Exception:  # keep the server up; the next run tries again
        logger.exception("Deleting old recordings failed")


async def clean_up_daily() -> None:
    """Once a day, while the server runs (the first run is at start-up)."""
    while True:
        await asyncio.sleep(CLEAN_UP_EVERY_SECONDS)
        await clean_up()
