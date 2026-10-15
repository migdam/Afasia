"""Your data: download all of it, or delete your account with it (P1-6c1)."""
import json
from pathlib import Path

from app.core.config import settings
from app.db.database import SessionLocal
from app.db import models
from test_recordings import WEBM, an_exercise_of, register, upload

PASSWORD = "correct horse battery"


def set_up_someone(client, username):
    """An account with a finished answer, a plan, consents and a recording."""
    auth = register(client, username)
    client.put("/api/v1/users/consents", headers=auth, json={"recordings": True})
    exercise = an_exercise_of(client, auth)
    client.post(f"/api/v1/therapy/exercises/{exercise}/answer", headers=auth,
                json={"answer": "hello", "time_taken_seconds": 3})
    client.post("/api/v1/users/scheduled-sessions", headers=auth,
                json={"title": f"{username}'s plan", "scheduled_time": "2099-01-01T10:00:00", "exercise_type": "word_naming"})
    recording = upload(client, auth, exercise, WEBM).json()["id"]
    return auth, recording


def export(client, auth):
    return client.get("/api/v1/users/me/export", headers=auth)


def delete_account(client, auth, password=PASSWORD):
    return client.request("DELETE", "/api/v1/users/me", headers=auth, json={"password": password})


def test_the_export_holds_everything_about_you(client):
    pat, recording = set_up_someone(client, "pat")

    response = export(client, pat)

    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    data = response.json()
    assert data["account"]["username"] == "pat"
    assert data["consents"] == {"recordings": True, "speech_recognition": None}
    [session] = data["sessions"]
    [exercise] = session["exercises"]
    assert exercise["user_answer"] == "hello"
    assert data["scheduled_sessions"][0]["title"] == "pat's plan"
    assert [r["id"] for r in data["recordings"]] == [recording]
    assert {"progress", "badges"} <= set(data)


def test_the_export_holds_no_secrets_and_nobody_elses_data(client):
    pat, _ = set_up_someone(client, "pat")
    set_up_someone(client, "sam")

    text = export(client, pat).text

    for secret in ("hashed_password", "$2b$", "file_path", str(settings.UPLOAD_DIR)):
        assert secret not in text, secret
    assert "sam" not in text


def test_deleting_needs_your_password(client):
    pat, _ = set_up_someone(client, "pat")

    assert delete_account(client, pat, "not my password").status_code == 400

    assert export(client, pat).status_code == 200


def stored_files():
    return [p for p in Path(settings.UPLOAD_DIR).rglob("*") if p.is_file()]


def rows_of(user_id):
    with SessionLocal() as db:
        return {
            "users": db.query(models.User).filter_by(id=user_id).count(),
            "sessions": db.query(models.TherapySession).filter_by(user_id=user_id).count(),
            "progress": db.query(models.Progress).filter_by(user_id=user_id).count(),
            "badges": db.query(models.UserBadge).filter_by(user_id=user_id).count(),
            "plans": db.query(models.ScheduledSession).filter_by(user_id=user_id).count(),
            "recordings": db.query(models.AudioRecording).filter_by(user_id=user_id).count(),
            "consents": db.query(models.Consent).filter_by(user_id=user_id).count(),
            "cutoffs": db.query(models.LoginCutoff).filter_by(user_id=user_id).count(),
        }


def test_deleting_your_account_removes_everything_and_logs_you_out(client):
    pat, _ = set_up_someone(client, "pat")
    sam, _ = set_up_someone(client, "sam")
    client.post("/api/v1/users/password", headers=pat,
                json={"current_password": PASSWORD, "new_password": "another passphrase"})
    pat = {"Authorization": "Bearer " + client.post(
        "/api/v1/auth/login", json={"username": "pat", "password": "another passphrase"}).json()["access_token"]}
    pat_id = export(client, pat).json()["account"]["id"]
    files_before = stored_files()

    response = delete_account(client, pat, "another passphrase")

    assert response.status_code == 204
    assert "max-age=0" in response.headers["set-cookie"].lower()
    assert set(rows_of(pat_id).values()) == {0}
    assert len(stored_files()) == len(files_before) - 1  # pat's recording; sam's stays
    assert export(client, pat).status_code == 401
    assert client.post("/api/v1/auth/login", json={"username": "pat", "password": "another passphrase"}).status_code == 401
    assert json.loads(export(client, sam).text)["account"]["username"] == "sam"
