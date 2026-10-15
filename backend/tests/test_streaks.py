"""Streaks and the first-session badge count finished sessions only, and
sessions finishing at the same time can't miscount a streak (P2-9a)."""
from datetime import datetime, timedelta

from app.api.v1.endpoints import therapy
from app.db.database import SessionLocal
from app.db.models import TherapySession, User
from test_recordings import register

DAY0 = datetime(2026, 3, 2, 12, 0)


def start(client, auth):
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "pronunciation", "difficulty": "easy", "num_exercises": 1,
    }).json()
    exercise = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()[0]
    return session["id"], exercise["id"]


def finish(client, auth, monkeypatch, day):
    monkeypatch.setattr(therapy, "utcnow", lambda: DAY0 + timedelta(days=day))
    _, exercise = start(client, auth)
    client.post(f"/api/v1/therapy/exercises/{exercise}/answer", headers=auth,
                json={"answer": "", "time_taken_seconds": 3, "self_rating": "said_it"})


def profile(client, auth):
    return client.get("/api/v1/users/profile", headers=auth).json()


def badges(client, auth):
    return [b["badge_type"] for b in client.get("/api/v1/users/badges", headers=auth).json()]


def test_the_first_finished_session_earns_the_badge_after_one_left_unfinished(client, monkeypatch):
    pat = register(client, "pat")
    start(client, pat)  # left unfinished

    finish(client, pat, monkeypatch, 0)

    assert badges(client, pat) == ["first_session"]


def test_days_in_a_row_make_a_streak_and_a_gap_starts_again(client, monkeypatch):
    pat = register(client, "pat")
    for day in (0, 1, 1, 2):
        finish(client, pat, monkeypatch, day)
    assert (profile(client, pat)["current_streak"], profile(client, pat)["longest_streak"]) == (3, 3)

    finish(client, pat, monkeypatch, 4)

    assert (profile(client, pat)["current_streak"], profile(client, pat)["longest_streak"]) == (1, 3)


def test_a_session_finishing_while_another_does_still_counts_its_day(client, monkeypatch):
    pat = register(client, "pat")
    finish(client, pat, monkeypatch, 0)
    first, _ = start(client, pat)
    second, _ = start(client, pat)

    # Two requests at once: the second read the person before the first
    # finished (just before midnight), and finishes just after it.
    late, early = SessionLocal(), SessionLocal()
    try:
        stale = late.get(TherapySession, second)
        assert stale.user.current_streak == 1  # read now, before the other finishes

        monkeypatch.setattr(therapy, "utcnow", lambda: DAY0 + timedelta(days=1, hours=11, minutes=59))
        other = early.get(TherapySession, first)
        therapy.finish_session(early, other)
        early.commit()

        monkeypatch.setattr(therapy, "utcnow", lambda: DAY0 + timedelta(days=1, hours=12, minutes=1))
        therapy.finish_session(late, stale)
        late.commit()
    finally:
        late.close()
        early.close()

    assert profile(client, pat)["current_streak"] == 3
