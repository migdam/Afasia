"""Forgiving answer checks (U6, P2-5): case, spacing, punctuation and missing
Polish letters don't matter, and a near miss is called "almost"."""
import pytest

from app.answers import is_near_miss, normalize
from app.content import load_concepts
from test_recordings import register


@pytest.mark.parametrize("typed, expected", [
    ("  Kot ", "kot"),
    ("ŁÓŻKO", "łóżko"),
    ("lozko", "łóżko"),
    ("samochod", "samochód"),
    ("zolw", "żółw"),
    ("szczoteczka   do zebow", "szczoteczka do zębów"),
    ("thank you!", "thank you"),
])
def test_these_count_as_the_same_answer(typed, expected):
    assert normalize(typed) == normalize(expected)


@pytest.mark.parametrize("typed, expected, near", [
    ("kto", "kot", True),           # two letters swapped
    ("kubel", "kubek", True),       # one letter wrong
    ("parasl", "parasol", True),    # one letter missing
    ("telefn", "telefon", True),
    ("chrzaszcz", "chrząszcz", False),  # not a miss at all: equal once normalized
    ("pies", "kot", False),
    ("bicicle", "bicycle", True),
    ("bcycl", "bicycle", True),     # two misses in a long word
    ("ko", "kot", False),           # too short to guess at
])
def test_near_misses(typed, expected, near):
    assert is_near_miss(typed, expected) is near


def naming_exercise(client, auth, language):
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "word_naming", "difficulty": "easy",
        "language": language, "num_exercises": 12,
    }).json()
    return client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()


def answer(client, auth, exercise, text):
    return client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth,
                       json={"answer": text, "time_taken_seconds": 2}).json()


def word_for(exercise, language):
    for concept in load_concepts():
        wording = getattr(concept, language)
        if exercise["question"].endswith(wording.description):
            return wording.word
    raise AssertionError(exercise["question"])


def test_polish_without_its_special_letters_is_right(client):
    pat = register(client, "pat")
    exercises = naming_exercise(client, pat, "pl")
    plain = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")

    for exercise in exercises:
        word = word_for(exercise, "pl")
        result = answer(client, pat, exercise, f"  {word.translate(plain).upper()} ")
        assert result["is_correct"], word


def test_a_near_miss_is_wrong_but_called_almost(client):
    pat = register(client, "pat")
    exercise = naming_exercise(client, pat, "en")[0]
    word = word_for(exercise, "en")
    typo = word[1] + word[0] + word[2:]  # the first two letters swapped

    result = answer(client, pat, exercise, typo)

    assert result["is_correct"] is False
    assert result["almost"] is True


def test_a_plain_wrong_answer_is_not_almost(client):
    pat = register(client, "pat")
    exercise = naming_exercise(client, pat, "en")[0]

    result = answer(client, pat, exercise, "xyzzy")

    assert result["is_correct"] is False and result["almost"] is False
