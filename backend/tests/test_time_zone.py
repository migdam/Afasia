"""Streak days follow the person's own time zone (backlog P2-9b)."""
from datetime import datetime

from app import streaks
from app.api.v1.endpoints import therapy
from app.db.database import SessionLocal
from app.db.models import TimeZoneSetting
from test_recordings import register
from test_streaks import profile


def finish_at(client, auth, monkeypatch, when):
    monkeypatch.setattr(therapy, "utcnow", lambda: when)
    monkeypatch.setattr(streaks, "utcnow", lambda: when)  # the streak shown is today's (P2-9c)
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "pronunciation", "difficulty": "easy", "num_exercises": 1,
    }).json()
    exercise = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()[0]
    client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth,
                json={"answer": "", "time_taken_seconds": 3, "self_rating": "said_it"})


def set_zone(client, auth, zone):
    return client.put("/api/v1/users/time-zone", headers=auth, json={"time_zone": zone})


def test_just_after_midnight_in_poland_is_the_next_day(client, monkeypatch):
    pat = register(client, "pat")
    assert set_zone(client, pat, "Europe/Warsaw").status_code == 200

    finish_at(client, pat, monkeypatch, datetime(2026, 3, 2, 10, 0))   # 2 March, 11:00 in Warsaw
    finish_at(client, pat, monkeypatch, datetime(2026, 3, 2, 23, 30))  # 3 March, 00:30 in Warsaw

    assert profile(client, pat)["current_streak"] == 2


def test_without_a_time_zone_days_are_utc(client, monkeypatch):
    pat = register(client, "pat")

    finish_at(client, pat, monkeypatch, datetime(2026, 3, 2, 10, 0))
    finish_at(client, pat, monkeypatch, datetime(2026, 3, 2, 23, 30))

    assert profile(client, pat)["current_streak"] == 1


def test_only_real_time_zones_are_kept(client):
    pat = register(client, "pat")

    assert set_zone(client, pat, "Mars/Olympus").status_code == 422
    assert set_zone(client, pat, "x" * 100).status_code == 422
    assert client.get("/api/v1/users/time-zone", headers=pat).json() == {"time_zone": None}

    set_zone(client, pat, "Europe/Warsaw")
    assert client.get("/api/v1/users/time-zone", headers=pat).json() == {"time_zone": "Europe/Warsaw"}


def test_the_time_zone_is_exported_and_deleted_with_the_account(client):
    pat = register(client, "pat")
    set_zone(client, pat, "Europe/Warsaw")

    assert client.get("/api/v1/users/me/export", headers=pat).json()["time_zone"] == "Europe/Warsaw"

    assert client.request("DELETE", "/api/v1/users/me", headers=pat, json={"password": "correct horse battery"}).status_code == 204
    db = SessionLocal()
    try:
        assert db.query(TimeZoneSetting).count() == 0
    finally:
        db.close()
