"""Exercise content rules (loop/PROMPT.md, C4: a prompt never contains its answer)."""
import re
from pathlib import Path

import pytest

from app.api.v1.endpoints.therapy import EXERCISE_DATA
from app.db.models import ExerciseType

# Repetition shows the word to say, so its prompt contains the answer by design.
REPETITION = {ExerciseType.PRONUNCIATION}

ITEMS = [
    (exercise_type, difficulty, item)
    for exercise_type, levels in EXERCISE_DATA.items()
    if exercise_type not in REPETITION
    for difficulty, items in levels.items()
    for item in items
]


@pytest.mark.parametrize(
    "exercise_type, difficulty, item",
    ITEMS,
    ids=[f"{t.value}-{d.value}-{item['answer']}" for t, d, item in ITEMS],
)
def test_prompts_do_not_contain_their_answer(exercise_type, difficulty, item):
    answer = re.escape(item["answer"])

    assert not re.search(rf"\b{answer}\b", item["question"], re.IGNORECASE)


FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
ALL_ITEMS = [item for levels in EXERCISE_DATA.values() for items in levels.values() for item in items]


@pytest.mark.parametrize("key", ["image", "audio"])
def test_every_referenced_asset_exists(key):
    # A missing file shows up as broken media in the exercise.
    missing = [item[key] for item in ALL_ITEMS if key in item and not (FRONTEND / item[key].lstrip("/")).is_file()]

    assert not missing, f"missing {key} files: {missing}"
