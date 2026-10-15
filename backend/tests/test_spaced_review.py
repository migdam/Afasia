"""Items answered right come back after growing gaps (C3, backlog P2-8b)."""
from datetime import timedelta

import pytest

from app.api.v1.endpoints import therapy
from app.content import naming_items
from app.core.clock import utcnow
from app.db.models import DifficultyLevel
from test_recordings import register

ANSWERS = {i["question"]: i["answer"] for i in naming_items(DifficultyLevel.EASY, "en")}


@pytest.fixture
def days_later(monkeypatch):
    start = utcnow()

    def move(days):
        monkeypatch.setattr(therapy, "utcnow", lambda: start + timedelta(days=days))
    return move


def start(client, auth, exercise_type="word_naming", count=1):
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": exercise_type, "difficulty": "easy", "num_exercises": count,
    }).json()
    return client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()


def name(client, auth, exercise, hints=0):
    for _ in range(hints):
        client.post(f"/api/v1/therapy/exercises/{exercise['id']}/hint", headers=auth)
    client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth,
                json={"answer": ANSWERS[exercise["question"]], "time_taken_seconds": 3})


def say(client, auth, exercise):
    client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth,
                json={"answer": "", "time_taken_seconds": 3, "self_rating": "said_it"})


def test_a_word_named_alone_waits_its_gap_then_comes_back_before_new_ones(client, days_later):
    pat = register(client, "pat")
    known = start(client, pat)[0]
    name(client, pat, known)

    days_later(1)
    assert known["question"] not in {start(client, pat)[0]["question"] for _ in range(10)}
    days_later(3)
    assert start(client, pat)[0]["question"] == known["question"]


def test_a_word_named_with_hints_comes_back_sooner(client, days_later):
    pat, sam = register(client, "pat"), register(client, "sam")
    helped = start(client, pat)[0]
    name(client, pat, helped, hints=1)
    alone = start(client, sam)[0]
    name(client, sam, alone)

    days_later(1.5)

    assert start(client, pat)[0]["question"] == helped["question"]
    assert start(client, sam)[0]["question"] != alone["question"]


def test_the_better_an_item_is_known_the_longer_it_waits(client, days_later):
    pat = register(client, "pat")
    for exercise in start(client, pat, "pronunciation", count=3):  # the three easy phrases
        say(client, pat, exercise)
    twice = start(client, pat, "pronunciation")[0]
    say(client, pat, twice)

    days_later(3)  # past the gap after one success, not after two

    assert twice["question"] not in {start(client, pat, "pronunciation")[0]["question"] for _ in range(10)}
