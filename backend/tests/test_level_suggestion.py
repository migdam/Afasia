"""Suggest an easier or harder level from recent scores (C3, backlog P2-8c).
Only a suggestion: the person chooses."""
import pytest

from app.core.config import settings
from test_recordings import register


def finish(client, auth, score_right, difficulty="easy", exercise_type="pronunciation"):
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": exercise_type, "difficulty": difficulty, "num_exercises": 1,
    }).json()
    exercise = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()[0]
    client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth, json={
        "answer": "", "time_taken_seconds": 3, "self_rating": "said_it" if score_right else "not_yet",
    })


def suggestion(client, auth, difficulty="easy", exercise_type="pronunciation"):
    response = client.get("/api/v1/therapy/level-suggestion", headers=auth,
                          params={"exercise_type": exercise_type, "difficulty": difficulty})
    assert response.status_code == 200
    return response.json()


def test_three_good_sessions_suggest_a_harder_level(client):
    pat = register(client, "pat")
    for _ in range(3):
        finish(client, pat, True)

    assert suggestion(client, pat) == {"difficulty": "medium", "direction": "harder"}


def test_three_hard_sessions_suggest_an_easier_level(client):
    pat = register(client, "pat")
    for _ in range(3):
        finish(client, pat, False, difficulty="medium")

    assert suggestion(client, pat, "medium") == {"difficulty": "easy", "direction": "easier"}


@pytest.mark.parametrize("results", [[True, True], [True, False, True]])
def test_too_few_sessions_or_a_middling_score_suggest_nothing(client, results):
    pat = register(client, "pat")
    for right in results:
        finish(client, pat, right)

    assert suggestion(client, pat) == {"difficulty": None, "direction": None}


def test_nothing_beyond_the_easiest_or_hardest_level(client):
    pat = register(client, "pat")
    for _ in range(3):
        finish(client, pat, True, difficulty="hard")
        finish(client, pat, False, difficulty="easy")

    assert suggestion(client, pat, "hard")["difficulty"] is None
    assert suggestion(client, pat, "easy")["difficulty"] is None


def test_only_the_latest_sessions_of_that_type_and_person_count(client):
    pat, sam = register(client, "pat"), register(client, "sam")
    for _ in range(3):
        finish(client, pat, False)
    for _ in range(3):
        finish(client, pat, True)
        finish(client, sam, False)

    assert suggestion(client, pat)["direction"] == "harder"
    assert suggestion(client, pat, exercise_type="word_naming")["direction"] is None


def test_the_thresholds_are_settings(client, monkeypatch):
    monkeypatch.setattr(settings, "LEVEL_WINDOW", 1)
    pat = register(client, "pat")
    finish(client, pat, True)

    assert suggestion(client, pat)["direction"] == "harder"
