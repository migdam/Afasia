"""Pronunciation is judged by the person's own rating (C5, P2-7a)."""
from test_recordings import WEBM, register


def pronunciation(client, auth):
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "pronunciation", "difficulty": "easy", "num_exercises": 1,
    }).json()
    return client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()[0]


def rate(client, auth, exercise, rating, heard=""):
    return client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth,
                       json={"answer": heard, "time_taken_seconds": 4, "self_rating": rating})


def test_i_said_it_counts_whatever_the_recognizer_heard(client):
    pat = register(client, "pat")

    result = rate(client, pat, pronunciation(client, pat), "said_it", heard="something else").json()

    assert result["is_correct"] is True


def test_not_yet_is_not_counted(client):
    pat = register(client, "pat")

    result = rate(client, pat, pronunciation(client, pat), "not_yet").json()

    assert result["is_correct"] is False and result["almost"] is False


def test_only_known_ratings(client):
    pat = register(client, "pat")

    assert rate(client, pat, pronunciation(client, pat), "great").status_code == 422


def test_what_the_recognizer_heard_is_kept_with_the_recording(client):
    pat = register(client, "pat")
    client.put("/api/v1/users/consents", headers=pat, json={"recordings": True})
    exercise = pronunciation(client, pat)

    response = client.post(
        f"/api/v1/users/audio/upload?exercise_id={exercise['id']}", headers=pat,
        files={"audio": ("recording", WEBM, "audio/webm")}, data={"transcription": "hello"},
    )

    assert response.status_code == 200
    recordings = client.get("/api/v1/users/me/export", headers=pat).json()["recordings"]
    assert recordings[0]["transcription"] == "hello"
