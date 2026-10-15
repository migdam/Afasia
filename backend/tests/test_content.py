"""Exercise content rules (loop/PROMPT.md, C4: a prompt never contains its answer)."""
import re

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
