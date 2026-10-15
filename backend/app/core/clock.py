"""The app's clock, in UTC.

The database columns hold UTC times without an offset ("naive"), because
changing their type needs migrations (backlog P3-1). So inside the app
times are naive UTC, and the API converts at its edges: times it receives
become naive UTC, and times it sends carry +00:00 (schemas.UTCDateTime), so
browsers show them in the person's own time zone.
"""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Now, as naive UTC. (The standard library's own shortcut for this is
    deprecated since Python 3.12.)"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_naive_utc(value: datetime) -> datetime:
    """A time as naive UTC; one without an offset is taken to be UTC already."""
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def as_utc(value: datetime) -> datetime:
    """A naive UTC time with its offset, for sending."""
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
