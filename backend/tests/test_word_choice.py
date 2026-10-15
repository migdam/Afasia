"""Choosing the word instead of typing it (U6, P2-6a)."""
from app.content import load_concepts
from test_recordings import register

PL_WORDS = {c.pl.word for c in load_concepts()}


def naming(client, auth, language="en", difficulty="easy"):
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "word_naming", "difficulty": difficulty,
        "language": language, "num_exercises": 1,
    }).json()
    return client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()[0]


def choices(client, auth, exercise):
    return client.post(f"/api/v1/therapy/exercises/{exercise['id']}/choices", headers=auth)


def answer(client, auth, exercise, text):
    return client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth,
                       json={"answer": text, "time_taken_seconds": 2}).json()


def word_for(exercise, language):
    for concept in load_concepts():
        wording = getattr(concept, language)
        if exercise["question"].endswith(wording.description):
            return wording
    raise AssertionError(exercise["question"])


def test_four_different_words_in_the_sessions_language_one_of_them_right(client):
    pat = register(client, "pat")
    exercise = naming(client, pat, "pl")

    words = choices(client, pat, exercise).json()["choices"]

    assert len(words) == len(set(words)) == 4
    assert word_for(exercise, "pl").word in words
    assert set(words) <= PL_WORDS


def test_asking_again_gives_the_same_choices(client):
    pat = register(client, "pat")
    exercise = naming(client, pat)

    assert choices(client, pat, exercise).json() == choices(client, pat, exercise).json()


def test_choosing_counts_but_earns_less_than_recalling(client):
    pat = register(client, "pat")
    exercise = naming(client, pat)
    choices(client, pat, exercise)

    result = answer(client, pat, exercise, word_for(exercise, "en").word)

    assert result["is_correct"] and result["choices_shown"]
    assert client.get("/api/v1/users/profile", headers=pat).json()["total_points"] == 5  # half of 10, pending review
    exported = client.get("/api/v1/users/me/export", headers=pat).json()["sessions"][0]["exercises"][0]
    assert exported["choices_shown"] is True


def test_no_choices_for_other_types_after_answering_or_for_others(client):
    pat, sam = register(client, "pat"), register(client, "sam")
    exercise = naming(client, pat)
    session = client.post("/api/v1/therapy/sessions", headers=pat, json={
        "title": "t", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": 1,
    }).json()
    sentence = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=pat).json()[0]

    assert choices(client, sam, exercise).status_code == 404
    assert choices(client, pat, sentence).status_code == 422
    answer(client, pat, exercise, "anything")
    assert choices(client, pat, exercise).status_code == 409
