"""Streaks of practice days (backlog P2-9, U10).

A streak counts the days on which the person finished a session, in their
own time zone (P2-9b). Up to STREAK_REST_DAYS days off in a row don't break
it (P2-9c): people get ill and go to hospital, and many practise a few times
a week. It is worked out from those days rather than kept as a running
count, so sessions finishing at the same time can't miscount it (P2-9a).
"""
from datetime import date, datetime, timezone, tzinfo
from typing import Iterable, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .core.clock import as_utc, utcnow
from .core.config import settings


def zone(name: Optional[str]) -> tzinfo:
    """A time zone by its IANA name; UTC when there is none, or when the name
    is no longer known, rather than failing."""
    if name:
        try:
            return ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return timezone.utc


def local_day(moment: datetime, in_zone: tzinfo) -> date:
    """The date of a (naive UTC) time in a time zone."""
    return as_utc(moment).astimezone(in_zone).date()


def goes_on(last_day: date, day: date) -> bool:
    """Whether a streak whose last practice day was last_day can go on on
    day: no more than STREAK_REST_DAYS days off in between."""
    return (day - last_day).days - 1 <= settings.STREAK_REST_DAYS


def streaks(days: Iterable[date], today: date) -> tuple:
    """The current streak and the longest one, in practice days, from the
    dates with a finished session. The current one is 0 once it can no
    longer go on today."""
    longest = run = 0
    previous = None
    for day in sorted(set(days)):
        run = run + 1 if previous and goes_on(previous, day) else 1
        longest = max(longest, run)
        previous = day
    current = run if previous and goes_on(previous, today) else 0
    return current, longest


def streak_today(counted: int, last_practice: Optional[datetime], zone_name: Optional[str]) -> int:
    """A streak counted when the last session finished, as it stands today:
    0 once more days have passed without practice than a streak allows."""
    if not counted or not last_practice:
        return counted or 0
    in_zone = zone(zone_name)
    return counted if goes_on(local_day(last_practice, in_zone), local_day(utcnow(), in_zone)) else 0
