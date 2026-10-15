"""Picking a session's exercises from the content pool."""
import threading

import pytest

from app.api.v1.endpoints.therapy import EXERCISE_DATA, generate_exercises
from app.db.models import DifficultyLevel, ExerciseType

ITEM = {"question": "The sky is ___", "answer": "blue", "options": ["blue", "red"]}


def call_with_timeout(fn, seconds=5):
    """Call fn in a daemon thread, failing instead of hanging if it doesn't return."""
    outcome = {}

    def run():
        try:
            outcome["value"] = fn()
        except Exception as error:  # noqa: BLE001 - handed back to the test
            outcome["error"] = error

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(seconds)
    assert not worker.is_alive(), f"did not return within {seconds} s"
    return outcome


def test_a_small_pool_is_repeated_to_the_requested_count(monkeypatch):
    monkeypatch.setitem(EXERCISE_DATA, ExerciseType.SENTENCE_COMPLETION, {DifficultyLevel.EASY: [ITEM]})

    outcome = call_with_timeout(
        lambda: generate_exercises(ExerciseType.SENTENCE_COMPLETION, DifficultyLevel.EASY, 3)
    )

    assert outcome["value"] == [ITEM, ITEM, ITEM]


@pytest.mark.parametrize(
    "pool",
    [{}, {DifficultyLevel.MEDIUM: [ITEM]}],
    ids=["no-content-for-the-type", "only-another-difficulty"],
)
def test_no_content_for_the_type_and_difficulty_raises_instead_of_hanging(monkeypatch, pool):
    monkeypatch.setitem(EXERCISE_DATA, ExerciseType.IMAGE_RECOGNITION, pool)

    outcome = call_with_timeout(
        lambda: generate_exercises(ExerciseType.IMAGE_RECOGNITION, DifficultyLevel.EASY, 3)
    )

    assert isinstance(outcome.get("error"), LookupError)
