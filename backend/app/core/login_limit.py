"""Slows down password guessing.

Wrong passwords are counted per username and client address: after
LOGIN_MAX_FAILURES within LOGIN_LOCK_MINUTES, that address must wait. So a
stranger guessing someone's password doesn't lock its owner out. A looser
limit per account, LOGIN_MAX_FAILURES_PER_ACCOUNT, still stops guessing
spread over many addresses.

The client address is the one the server sees. Behind a proxy that is the
proxy's, unless the server is told to trust the proxy's X-Forwarded-For
header (docker-compose.yml does this for its nginx).

The counts are kept in memory, so they are per process: with several
workers each one counts on its own, and a restart forgets them.
"""
import time
from threading import Lock

from .config import settings

_failures: dict[tuple, list[float]] = {}
_lock = Lock()


def _keys(username: str, client: str) -> tuple[tuple, tuple]:
    name = username.strip().lower()
    return ("client", name, client), ("account", name)


def _recent(key: tuple, now: float) -> list[float]:
    window = settings.LOGIN_LOCK_MINUTES * 60
    times = [t for t in _failures.get(key, []) if now - t < window]
    if times:
        _failures[key] = times
    else:
        _failures.pop(key, None)
    return times


def retry_after(username: str, client: str) -> int:
    """Seconds until this client may try this username again; 0 if it may try now."""
    now = time.monotonic()
    window = settings.LOGIN_LOCK_MINUTES * 60
    limits = (settings.LOGIN_MAX_FAILURES, settings.LOGIN_MAX_FAILURES_PER_ACCOUNT)
    wait = 0
    with _lock:
        for key, limit in zip(_keys(username, client), limits):
            times = _recent(key, now)
            if len(times) >= limit:
                # Free again once enough of the failures leave the window.
                wait = max(wait, int(times[-limit] + window - now) + 1)
    return wait


def record_failure(username: str, client: str) -> None:
    now = time.monotonic()
    with _lock:
        for key in _keys(username, client):
            _failures[key] = _recent(key, now) + [now]


def record_success(username: str, client: str) -> None:
    """A right password clears this client's count; the account's count stays."""
    with _lock:
        _failures.pop(_keys(username, client)[0], None)


def reset() -> None:
    """Forget every record (for tests)."""
    with _lock:
        _failures.clear()
