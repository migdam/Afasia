"""Days off don't break a streak, and the streak shown is today's
(backlog P2-9c, U10: people get ill and go to hospital)."""
from datetime import datetime, timedelta

import pytest

from app import streaks
from app.api.v1.endpoints import therapy
from app.core.config import settings
from test_recordings import register

DAY0 = datetime(2026, 3, 2, 12, 0)  # a Monday, noon UTC


@pytest.fixture
def on_day(monkeypatch):
    """Move the app's clock to noon on a day after DAY0."""
    def move(day):
        moment = DAY0 + timedelta(days=day)
        monkeypatch.setattr(therapy, "utcnow", lambda: moment)
        monkeypatch.setattr(streaks, "utcnow", lambda: moment)
    return move


def practise(client, auth, on_day, *days):
    for day in days:
        on_day(day)
        session = client.post("/api/v1/therapy/sessions", headers=auth, json={
            "title": "t", "exercise_type": "pronunciation", "difficulty": "easy", "num_exercises": 1,
        }).json()
        exercise = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()[0]
        client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth,
                    json={"answer": "", "time_taken_seconds": 3, "self_rating": "said_it"})


def shown(client, auth):
    profile = client.get("/api/v1/users/profile", headers=auth).json()
    progress = client.get("/api/v1/users/progress", headers=auth).json()
    assert (progress["current_streak"], progress["longest_streak"]) == (
        profile["current_streak"], profile["longest_streak"])
    return profile["current_streak"], profile["longest_streak"]


def test_a_day_or_two_off_doesnt_break_a_streak(client, on_day):
    pat = register(client, "pat")

    practise(client, pat, on_day, 0, 2, 4, 7)  # Monday, Wednesday, Friday, Monday

    assert shown(client, pat) == (4, 4)


def test_a_longer_break_starts_a_new_streak(client, on_day):
    pat = register(client, "pat")

    practise(client, pat, on_day, 0, 1, 5)  # three days off before the last

    assert shown(client, pat) == (1, 2)


def test_the_streak_shown_ends_after_a_longer_break_and_the_longest_stays(client, on_day):
    pat = register(client, "pat")
    practise(client, pat, on_day, 0, 1)

    on_day(4)  # two days off so far: practising today would still carry it on
    assert shown(client, pat) == (2, 2)

    on_day(5)  # three days off
    assert shown(client, pat) == (0, 2)


def test_the_days_off_allowed_are_a_setting(client, on_day, monkeypatch):
    monkeypatch.setattr(settings, "STREAK_REST_DAYS", 0)
    pat = register(client, "pat")

    practise(client, pat, on_day, 0, 2)

    assert shown(client, pat) == (1, 1)
