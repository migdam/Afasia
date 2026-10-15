"""Letter tiles: building the word from its letters instead of typing (P2-6b)."""
from collections import Counter

from test_recordings import register
from test_word_choice import answer, naming, word_for


def tiles(client, auth, exercise):
    return client.post(f"/api/v1/therapy/exercises/{exercise['id']}/tiles", headers=auth)


def test_the_tiles_are_the_letters_of_the_word_in_the_sessions_language(client):
    pat = register(client, "pat")
    exercise = naming(client, pat, "pl")

    letters = tiles(client, pat, exercise).json()["tiles"]

    assert Counter(letters) == Counter(word_for(exercise, "pl").word)


def test_asking_again_gives_the_same_order(client):
    pat = register(client, "pat")
    exercise = naming(client, pat)

    assert tiles(client, pat, exercise).json() == tiles(client, pat, exercise).json()


def test_tiles_count_but_earn_less_than_recalling(client):
    pat = register(client, "pat")
    exercise = naming(client, pat)
    tiles(client, pat, exercise)

    result = answer(client, pat, exercise, word_for(exercise, "en").word)

    assert result["is_correct"] and result["tiles_used"]
    assert client.get("/api/v1/users/profile", headers=pat).json()["total_points"] == 5  # pending review
    exported = client.get("/api/v1/users/me/export", headers=pat).json()["sessions"][0]["exercises"][0]
    assert exported["tiles_used"] is True


def test_no_tiles_for_other_types_after_answering_or_for_others(client):
    pat, sam = register(client, "pat"), register(client, "sam")
    exercise = naming(client, pat)
    session = client.post("/api/v1/therapy/sessions", headers=pat, json={
        "title": "t", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": 1,
    }).json()
    sentence = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=pat).json()[0]

    assert tiles(client, sam, exercise).status_code == 404
    assert tiles(client, pat, sentence).status_code == 422
    answer(client, pat, exercise, "anything")
    assert tiles(client, pat, exercise).status_code == 409
