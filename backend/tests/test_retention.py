"""Recordings older than RECORDING_RETENTION_DAYS are deleted (P1-6e)."""
import io
from datetime import datetime, timedelta
from pathlib import Path

from app import cli
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import AudioRecording
from test_recordings import an_exercise_of, register, upload


def make_recordings(client, ages_in_days):
    """One recording per age; returns their ids, oldest first as given."""
    auth = register(client, "pat")
    client.put("/api/v1/users/consents", headers=auth, json={"recordings": True})
    exercise = an_exercise_of(client, auth)
    ids = [upload(client, auth, exercise).json()["id"] for _ in ages_in_days]
    with SessionLocal() as db:
        for recording_id, age in zip(ids, ages_in_days):
            db.get(AudioRecording, recording_id).created_at = datetime.utcnow() - timedelta(days=age)
        db.commit()
    return ids


def surviving(ids):
    with SessionLocal() as db:
        rows = [db.get(AudioRecording, i) for i in ids]
        return [(row is not None) and Path(row.file_path).exists() for row in rows]


def files(ids):
    with SessionLocal() as db:
        return [Path(db.get(AudioRecording, i).file_path) for i in ids]


def run_cli(monkeypatch, capsys, *args):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    code = cli.main(["delete-old-recordings", *args])
    return code, capsys.readouterr().out


def test_the_command_deletes_recordings_older_than_the_limit_with_their_files(client, monkeypatch, capsys):
    ids = make_recordings(client, [40, 10])
    old_file = files(ids)[0]

    code, out = run_cli(monkeypatch, capsys, "--days", "30")

    assert code == 0
    assert "1" in out
    assert surviving(ids) == [False, True]
    assert not old_file.exists()


def test_by_default_recordings_are_kept_until_deleted(client, monkeypatch, capsys):
    ids = make_recordings(client, [400])

    code, out = run_cli(monkeypatch, capsys)

    assert code == 0
    assert "RECORDING_RETENTION_DAYS" in out
    assert surviving(ids) == [True]


def test_with_a_limit_set_the_server_cleans_up_when_it_starts(client, monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app

    ids = make_recordings(client, [40, 10])
    monkeypatch.setattr(settings, "RECORDING_RETENTION_DAYS", 30)

    with TestClient(app):
        pass

    assert surviving(ids) == [False, True]
