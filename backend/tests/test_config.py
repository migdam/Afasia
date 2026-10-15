"""Settings: where .env is read from, and how values are parsed."""
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import ROOT_ENV_FILE, Settings

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_env_file_is_read_from_the_repo_root():
    # The README copies .env.template to .env at the repository root.
    assert ROOT_ENV_FILE == REPO_ROOT / ".env"
    assert (REPO_ROOT / ".env.template").is_file()


def test_env_template_loads_as_is(monkeypatch):
    monkeypatch.delenv("SECRET_KEY")
    monkeypatch.delenv("BACKEND_CORS_ORIGINS", raising=False)

    settings = Settings(_env_file=REPO_ROOT / ".env.template")

    assert settings.SECRET_KEY
    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]


def test_unknown_env_file_keys_are_ignored(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET_KEY=from-file\nPOSTGRES_PASSWORD=compose-only\n")
    monkeypatch.delenv("SECRET_KEY")

    settings = Settings(_env_file=env_file)

    assert settings.SECRET_KEY == "from-file"
    assert not hasattr(settings, "POSTGRES_PASSWORD")


def test_cors_origins_from_comma_separated_env_var(monkeypatch):
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", " http://a.test , http://b.test,, ")

    settings = Settings(_env_file=None)

    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_secret_key_is_required(monkeypatch):
    monkeypatch.delenv("SECRET_KEY")

    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(_env_file=None)
