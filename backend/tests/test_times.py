"""Times are UTC, and say so (P1-8d).

The database keeps UTC without an offset (no migrations yet, P3-1); the
API turns times it receives into UTC and sends every time with +00:00, so
browsers show them in the person's own time zone.
"""
import re
from pathlib import Path

from test_recordings import register

APP = Path(__file__).resolve().parents[1] / "app"
UTC = re.compile(r"\+00:00$|Z$")


def plan(client, auth, when):
    return client.post("/api/v1/users/scheduled-sessions", headers=auth, json={
        "title": "plan", "scheduled_time": when, "exercise_type": "word_naming",
    })


def test_times_sent_with_an_offset_are_kept_as_that_moment(client):
    pat = register(client, "pat")

    created = plan(client, pat, "2099-06-01T10:00:00+02:00").json()

    assert created["scheduled_time"] == "2099-06-01T08:00:00+00:00"
    [listed] = client.get("/api/v1/users/scheduled-sessions", headers=pat).json()
    assert listed["scheduled_time"] == "2099-06-01T08:00:00+00:00"


def test_times_without_an_offset_are_taken_as_utc(client):
    pat = register(client, "pat")

    assert plan(client, pat, "2099-06-01T10:00:00").json()["scheduled_time"] == "2099-06-01T10:00:00+00:00"


def test_every_time_the_api_sends_says_it_is_utc(client):
    pat = register(client, "pat")
    plan(client, pat, "2099-06-01T10:00:00Z")
    session = client.post("/api/v1/therapy/sessions", headers=pat, json={
        "title": "t", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": 1,
    }).json()

    times = [
        client.get("/api/v1/users/profile", headers=pat).json()["created_at"],
        session["started_at"],
        client.get("/api/v1/users/scheduled-sessions", headers=pat).json()[0]["created_at"],
    ]
    export = client.get("/api/v1/users/me/export", headers=pat).json()
    times += [export["exported_at"], export["account"]["created_at"], export["sessions"][0]["started_at"]]

    assert all(UTC.search(t) for t in times), times


def test_no_deprecated_utcnow_in_the_app():
    # app/core/clock.py has the app's own utcnow(); the standard library's
    # datetime.utcnow is deprecated since Python 3.12.
    users = [str(p.relative_to(APP)) for p in APP.rglob("*.py") if "datetime.utcnow" in p.read_text()]

    assert users == [], users
