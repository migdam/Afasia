"""Therapy sessions: the last answer completes a session, scored once by the server."""
from datetime import datetime, timedelta

import pytest

from app.api.v1.endpoints.therapy import EXERCISE_DATA
from app.db.database import SessionLocal
from app.db.models import ExerciseType, TherapySession

ANSWERS = {
    item["question"]: item["answer"]
    for levels in EXERCISE_DATA.values()
    for items in levels.values()
    for item in items
}


@pytest.fixture
def auth(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "pat@example.com", "username": "pat", "password": "correct horse battery"},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def start_session(client, auth):
    """Start an easy sentence-completion session: 3 exercises, 10 points each."""
    response = client.post(
        "/api/v1/therapy/sessions",
        headers=auth,
        json={
            "title": "Practice",
            "exercise_type": "sentence_completion",
            "difficulty": "easy",
            "num_exercises": 3,
        },
    )
    assert response.status_code == 200, response.text
    session_id = response.json()["id"]
    exercises = client.get(f"/api/v1/therapy/sessions/{session_id}/exercises", headers=auth)
    return session_id, exercises.json()


def answer(client, auth, exercise, correct=True):
    reply = ANSWERS[exercise["question"]] if correct else "not the answer"
    return client.post(
        f"/api/v1/therapy/exercises/{exercise['id']}/answer",
        headers=auth,
        json={"answer": reply, "time_taken_seconds": 5},
    )


def get_session(client, auth, session_id):
    return client.get(f"/api/v1/therapy/sessions/{session_id}", headers=auth).json()


def get_points_and_history(client, auth):
    points = client.get("/api/v1/users/profile", headers=auth).json()["total_points"]
    history = client.get("/api/v1/users/progress", headers=auth).json()["progress_history"]
    return points, history


def test_a_type_without_content_is_refused_and_creates_nothing(client, auth, monkeypatch):
    monkeypatch.setitem(EXERCISE_DATA, ExerciseType.IMAGE_RECOGNITION, {})

    response = client.post(
        "/api/v1/therapy/sessions",
        headers=auth,
        json={
            "title": "Practice",
            "exercise_type": "image_recognition",
            "difficulty": "easy",
            "num_exercises": 3,
        },
    )

    assert response.status_code == 422
    assert "image_recognition" in response.json()["detail"]
    assert client.get("/api/v1/therapy/sessions", headers=auth).json() == []


def test_the_last_answer_completes_and_scores_the_session(client, auth):
    session_id, exercises = start_session(client, auth)

    for exercise, correct in zip(exercises, [True, True, False]):
        assert answer(client, auth, exercise, correct).status_code == 200

    session = get_session(client, auth, session_id)
    assert session["is_completed"]
    assert session["completed_exercises"] == 3
    assert session["score"] == pytest.approx(200 / 3)


def test_a_completed_session_adds_up_points_and_records_progress_once(client, auth):
    _, exercises = start_session(client, auth)

    for exercise, correct in zip(exercises, [True, True, False]):
        answer(client, auth, exercise, correct)

    points, history = get_points_and_history(client, auth)
    assert points == 20  # two correct easy answers
    assert len(history) == 1
    assert history[0]["points_earned"] == 20
    assert history[0]["exercises_completed"] == 3
    assert client.get("/api/v1/users/profile", headers=auth).json()["current_streak"] == 1


def test_an_answered_exercise_cant_be_answered_again(client, auth):
    _, exercises = start_session(client, auth)
    answer(client, auth, exercises[0], correct=False)

    assert answer(client, auth, exercises[0], correct=True).status_code == 409

    for exercise in exercises[1:]:
        answer(client, auth, exercise)
    for exercise in exercises:
        assert answer(client, auth, exercise).status_code == 409

    points, history = get_points_and_history(client, auth)
    assert points == 20
    assert len(history) == 1


def test_complete_returns_the_server_result_and_ignores_the_client(client, auth):
    session_id, exercises = start_session(client, auth)
    for exercise in exercises:
        answer(client, auth, exercise)

    response = client.post(
        f"/api/v1/therapy/sessions/{session_id}/complete",
        headers=auth,
        json={"score": 0, "duration_seconds": 99999},
    )

    assert response.status_code == 200
    assert response.json()["score"] == 100
    assert response.json()["duration_seconds"] != 99999
    assert get_session(client, auth, session_id)["score"] == 100


def test_complete_before_the_last_answer_is_refused(client, auth):
    session_id, exercises = start_session(client, auth)
    answer(client, auth, exercises[0])

    response = client.post(f"/api/v1/therapy/sessions/{session_id}/complete", headers=auth)

    assert response.status_code == 409
    assert not get_session(client, auth, session_id)["is_completed"]


def test_duration_runs_from_the_start_to_the_last_answer(client, auth):
    session_id, exercises = start_session(client, auth)
    with SessionLocal() as db:
        db.get(TherapySession, session_id).started_at = datetime.utcnow() - timedelta(seconds=90)
        db.commit()

    for exercise in exercises:
        answer(client, auth, exercise)

    session = get_session(client, auth, session_id)
    _, history = get_points_and_history(client, auth)
    assert 90 <= session["duration_seconds"] <= 92
    assert history[0]["total_time_seconds"] == session["duration_seconds"]
