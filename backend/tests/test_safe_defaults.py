"""Safe defaults: debug off, no guessable signing key, no configuration on show (P1-8a)."""
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings

TEMPLATE = Path(__file__).resolve().parents[2] / ".env.template"
GOOD_KEY = "k" * 32


def template_key():
    line = next(l for l in TEMPLATE.read_text().splitlines() if l.startswith("SECRET_KEY="))
    return line.split("=", 1)[1]


def test_debug_is_off_unless_asked_for(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", GOOD_KEY)

    assert Settings(_env_file=None).DEBUG is False


def test_the_example_key_from_the_template_is_refused(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", template_key())

    with pytest.raises(ValidationError, match="openssl rand -hex 32"):
        Settings(_env_file=None)


def test_keys_shorter_than_32_bytes_are_refused(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "k" * 31)
    with pytest.raises(ValidationError, match="32 bytes"):
        Settings(_env_file=None)

    monkeypatch.setenv("SECRET_KEY", GOOD_KEY)
    assert Settings(_env_file=None).SECRET_KEY == GOOD_KEY


def test_the_detailed_health_check_shows_no_settings_and_really_checks_the_database(client):
    body = client.get("/health/detailed").json()

    assert "debug" not in body
    assert body["database"] == "ok"


def test_the_detailed_health_check_says_when_the_database_is_down(client, monkeypatch):
    import app.main

    class BrokenEngine:
        def connect(self):
            raise OSError("database unreachable")

    monkeypatch.setattr(app.main, "engine", BrokenEngine())

    response = client.get("/health/detailed")

    assert response.status_code == 503
    assert response.json()["database"] == "unavailable"
