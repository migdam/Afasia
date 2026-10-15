"""Voice recordings: private to their owner, checked on the way in (backlog P1-2)."""
from pathlib import Path

import pytest

from app.core.config import settings

WEBM = b"\x1aE\xdf\xa3" + b"\x00" * 64  # the start of a WebM file, as browsers record it


def register(client, username):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": "correct horse battery"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def an_exercise_of(client, auth):
    session = client.post(
        "/api/v1/therapy/sessions",
        headers=auth,
        json={"title": "t", "exercise_type": "pronunciation", "difficulty": "easy", "num_exercises": 1},
    ).json()
    return client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()[0]["id"]


def upload(client, auth, exercise_id, content=WEBM, content_type="audio/webm;codecs=opus"):
    return client.post(
        f"/api/v1/users/audio/upload?exercise_id={exercise_id}",
        headers=auth,
        files={"audio": ("recording", content, content_type)},
    )


@pytest.fixture
def pat(client):
    auth = register(client, "pat")
    return auth, an_exercise_of(client, auth)


def stored_files():
    return sorted(p for p in Path(settings.UPLOAD_DIR).rglob("*") if p.is_file())


def test_only_the_owner_can_play_a_recording(client, pat):
    auth, exercise_id = pat
    response = upload(client, auth, exercise_id)
    assert response.status_code == 200, response.text
    recording_id = response.json()["id"]
    assert "file_path" not in response.json()

    mine = client.get(f"/api/v1/users/audio/{recording_id}", headers=auth)
    assert mine.status_code == 200
    assert mine.headers["content-type"].startswith("audio/webm")
    assert mine.content == WEBM

    someone_else = register(client, "sam")
    assert client.get(f"/api/v1/users/audio/{recording_id}", headers=someone_else).status_code == 404
    assert client.get(f"/api/v1/users/audio/{recording_id}").status_code == 401


def test_recordings_are_stored_privately_under_random_names(client, pat):
    auth, exercise_id = pat
    before = stored_files()
    upload(client, auth, exercise_id)

    [path] = [p for p in stored_files() if p not in before]
    assert path.suffix == ".webm"
    assert path.is_relative_to(Path(settings.UPLOAD_DIR))
    assert len(path.stem) == 32  # a random hex name, nothing about the user or exercise
    for public in (f"/uploads/audio/{path.name}", f"/uploads/{path.name}"):
        assert client.get(public).status_code == 404


def test_uploads_that_are_too_large_or_not_audio_are_refused(client, pat, monkeypatch):
    auth, exercise_id = pat
    before = stored_files()
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE", len(WEBM) - 1)
    assert upload(client, auth, exercise_id).status_code == 413
    monkeypatch.undo()

    assert upload(client, auth, exercise_id, b"<html>", "text/html").status_code == 415
    assert upload(client, auth, exercise_id, b"").status_code == 400
    assert stored_files() == before


def test_recordings_only_for_your_own_exercises(client, pat):
    _, exercise_id = pat
    someone_else = register(client, "sam")

    assert upload(client, someone_else, exercise_id).status_code == 404
