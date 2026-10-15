"""Slows down password guessing: too many wrong passwords lock a username for a while.

The record is kept in memory, so it is per process: with several workers each
one counts on its own, and a restart forgets it.
"""
import time
from threading import Lock

MAX_FAILURES = 5
WINDOW_SECONDS = 15 * 60

_failures: dict[str, list[float]] = {}
_lock = Lock()


def _key(username: str) -> str:
    return username.strip().lower()


def _recent(key: str, now: float) -> list[float]:
    times = [t for t in _failures.get(key, []) if now - t < WINDOW_SECONDS]
    if times:
        _failures[key] = times
    else:
        _failures.pop(key, None)
    return times


def retry_after(username: str) -> int:
    """Seconds until this username may try again; 0 if it may try now."""
    now = time.monotonic()
    with _lock:
        times = _recent(_key(username), now)
        if len(times) < MAX_FAILURES:
            return 0
        return max(1, int(times[0] + WINDOW_SECONDS - now) + 1)


def record_failure(username: str) -> None:
    now = time.monotonic()
    key = _key(username)
    with _lock:
        _failures[key] = _recent(key, now) + [now]


def record_success(username: str) -> None:
    with _lock:
        _failures.pop(_key(username), None)


def reset() -> None:
    """Forget every record (for tests)."""
    with _lock:
        _failures.clear()
