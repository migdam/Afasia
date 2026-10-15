"""Naming hints, one step at a time (P2-3a, U7, C1): what it means, then how
it starts, then the whole word. The level used is recorded, and points
depend on how independently the word was found."""
import pytest

from app.content import load_concepts
from test_recordings import register

BY_WORD = {getattr(c, lang).word: (c, lang) for c in load_concepts() for lang in ("en", "pl")}


def one_naming_exercise(client, auth, language="en"):
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "word_naming", "difficulty": "easy",
        "language": language, "num_exercises": 1,
    }).json()
    return session, client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()[0]


def hint(client, auth, exercise):
    return client.post(f"/api/v1/therapy/exercises/{exercise['id']}/hint", headers=auth)


def answer(client, auth, exercise, text):
    return client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth,
                       json={"answer": text, "time_taken_seconds": 5}).json()


def word_of(client, auth, exercise, language):
    # The prompt is the concept's description, so it tells which concept it is.
    for c in load_concepts():
        if exercise["question"].endswith(getattr(c, language).description):
            return getattr(c, language)
    raise AssertionError(exercise["question"])


@pytest.mark.parametrize("language", ["en", "pl"])
def test_three_hints_go_from_meaning_to_first_letter_to_the_word(client, language):
    pat = register(client, "pat")
    _, exercise = one_naming_exercise(client, pat, language)
    wording = word_of(client, pat, exercise, language)

    first, second, third = (hint(client, pat, exercise).json() for _ in range(3))

    assert first["level"] == 1 and wording.features.category in first["cue"]
    assert wording.word not in first["cue"]
    assert second["level"] == 2 and wording.word[0].upper() in second["cue"] and wording.word not in second["cue"]
    assert third["level"] == 3 and wording.word in third["cue"] and third["last"]
    assert hint(client, pat, exercise).status_code == 409  # nothing more to give


def test_the_hints_used_are_recorded_and_lower_the_points(client):
    pat = register(client, "pat")
    session, exercise = one_naming_exercise(client, pat)
    hint(client, pat, exercise)
    hint(client, pat, exercise)

    result = answer(client, pat, exercise, word_of(client, pat, exercise, "en").word)

    assert result["is_correct"] and result["cue_level"] == 2
    profile = client.get("/api/v1/users/profile", headers=pat).json()
    assert profile["total_points"] == 5  # easy is 10 points; with two hints, half (pending review)


def test_without_hints_the_points_are_whole(client):
    pat = register(client, "pat")
    _, exercise = one_naming_exercise(client, pat)

    result = answer(client, pat, exercise, word_of(client, pat, exercise, "en").word)

    assert result["cue_level"] == 0
    assert client.get("/api/v1/users/profile", headers=pat).json()["total_points"] == 10


def test_no_hints_after_answering_or_for_someone_elses_exercise(client):
    pat, sam = register(client, "pat"), register(client, "sam")
    _, exercise = one_naming_exercise(client, pat)

    assert hint(client, sam, exercise).status_code == 404
    answer(client, pat, exercise, "anything")
    assert hint(client, pat, exercise).status_code == 409


def test_only_naming_has_hints(client):
    pat = register(client, "pat")
    session = client.post("/api/v1/therapy/sessions", headers=pat, json={
        "title": "t", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": 1,
    }).json()
    exercise = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=pat).json()[0]

    assert hint(client, pat, exercise).status_code == 422


def test_the_level_shows_in_the_exercise_list_and_the_export(client):
    pat = register(client, "pat")
    session, exercise = one_naming_exercise(client, pat)
    hint(client, pat, exercise)

    [listed] = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=pat).json()
    exported = client.get("/api/v1/users/me/export", headers=pat).json()["sessions"][0]["exercises"][0]

    assert listed["cue_level"] == 1
    assert exported["cue_level"] == 1


@pytest.mark.parametrize("language", ["en", "pl"])
def test_no_concepts_first_two_hints_give_the_word_away(language):
    from app.content import gives_away, naming_cue

    leaks = [
        (getattr(c, language).word, level)
        for c in load_concepts() for level in (1, 2)
        if any(gives_away(naming_cue(language, getattr(c, language).word, level), a) for a in getattr(c, language).answers)
    ]

    assert leaks == []
