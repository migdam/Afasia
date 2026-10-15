"""Missed items come back in the next session (C3, backlog P2-8a)."""
from test_recordings import register


def start(client, auth, count=1, language="en"):
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "pronunciation", "difficulty": "easy",
        "num_exercises": count, "language": language,
    }).json()
    return client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()


def answer(client, auth, exercise, right):
    client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth, json={
        "answer": "", "time_taken_seconds": 3, "self_rating": "said_it" if right else "not_yet",
    })


def drawn(client, auth, times=30, language="en"):
    return {start(client, auth, language=language)[0]["question"] for _ in range(times)}


def test_a_missed_item_comes_back_in_the_next_session(client):
    pat = register(client, "pat")
    missed = start(client, pat)[0]
    answer(client, pat, missed, right=False)

    assert drawn(client, pat, times=5) == {missed["question"]}


def test_an_item_answered_right_since_is_drawn_at_random_again(client):
    pat = register(client, "pat")
    answer(client, pat, start(client, pat)[0], right=False)
    answer(client, pat, start(client, pat)[0], right=True)  # the same item, now said

    assert len(drawn(client, pat)) > 1


def test_at_most_half_a_session_is_review(client):
    pat = register(client, "pat")
    first, second, third = start(client, pat, count=3)  # the three easy phrases
    answer(client, pat, first, right=False)
    answer(client, pat, second, right=False)
    answer(client, pat, third, right=True)

    questions = [e["question"] for e in start(client, pat, count=2)]

    assert third["question"] in questions  # one review item, one other
    assert len(set(questions) & {first["question"], second["question"]}) == 1


def test_only_your_own_misses_in_the_same_language_come_back(client):
    pat, sam = register(client, "pat"), register(client, "sam")
    answer(client, pat, start(client, pat, language="pl")[0], right=False)

    assert len(drawn(client, sam)) > 1
    assert len(drawn(client, pat, language="en")) > 1
