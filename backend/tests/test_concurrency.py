"""Simultaneous requests: each answer counts once, and each session completes once."""
import threading

from app.api.v1.endpoints.therapy import EXERCISE_DATA

ANSWERS = {
    item["question"]: item["answer"]
    for levels in EXERCISE_DATA.values()
    for items in levels.values()
    for item in items
}
TRIALS = 10


def register(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "pat@example.com", "username": "pat", "password": "correct horse battery"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def start_session(client, auth, count):
    session = client.post(
        "/api/v1/therapy/sessions",
        headers=auth,
        json={"title": "t", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": count},
    ).json()
    return session["id"], client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()


def answer_at_once(client, auth, exercises):
    """Send one correct answer per exercise, all at the same moment."""
    codes, start = [], threading.Barrier(len(exercises))

    def submit(exercise):
        start.wait()
        response = client.post(
            f"/api/v1/therapy/exercises/{exercise['id']}/answer",
            headers=auth,
            json={"answer": ANSWERS[exercise["question"]], "time_taken_seconds": 1},
        )
        codes.append(response.status_code)

    threads = [threading.Thread(target=submit, args=(e,)) for e in exercises]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return sorted(codes)


def totals(client, auth):
    points = client.get("/api/v1/users/profile", headers=auth).json()["total_points"]
    records = client.get("/api/v1/users/progress", headers=auth).json()["progress_history"]
    return points, len(records)


def test_the_same_answer_sent_twice_at_once_counts_once(client):
    auth = register(client)

    for _ in range(TRIALS):
        _, exercises = start_session(client, auth, 1)
        assert answer_at_once(client, auth, exercises * 2) == [200, 409]

    assert totals(client, auth) == (10 * TRIALS, TRIALS)  # 10 points per session


def test_the_last_two_answers_at_once_complete_the_session_once(client):
    auth = register(client)

    for _ in range(TRIALS):
        session_id, exercises = start_session(client, auth, 2)
        assert answer_at_once(client, auth, exercises) == [200, 200]
        session = client.get(f"/api/v1/therapy/sessions/{session_id}", headers=auth).json()
        assert (session["is_completed"], session["completed_exercises"], session["score"]) == (True, 2, 100)

    assert totals(client, auth) == (20 * TRIALS, TRIALS)
