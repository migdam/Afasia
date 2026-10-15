"""Session size is bounded (P1-9): no empty or negative sessions, which can
never finish, and no huge ones that tie up the server and fill the database."""
import pytest

from app.db.database import SessionLocal
from app.db.models import TherapySession
from test_recordings import register


def start(client, auth, count):
    return client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": count,
    })


@pytest.mark.parametrize("count", [0, -5, 51, 20_000])
def test_sizes_outside_1_to_50_are_refused_and_nothing_is_created(client, count):
    pat = register(client, "pat")

    response = start(client, pat, count)

    assert response.status_code == 422
    with SessionLocal() as db:
        assert db.query(TherapySession).count() == 0


@pytest.mark.parametrize("count", [1, 5, 50])
def test_sizes_from_1_to_50_work(client, count):
    pat = register(client, "pat")

    session = start(client, pat, count).json()

    assert session["total_exercises"] == count
    exercises = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=pat).json()
    assert len(exercises) == count
