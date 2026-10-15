"""Every setting set in .env reaches the backend in Docker too (P1-8b).

Compose passes the backend only the variables listed under its
`environment`, so each setting must be listed there, taken from .env
(`${NAME...}`). A few are fixed by the Docker setup on purpose.
"""
from pathlib import Path

import re

import yaml

from app.core.config import Settings

COMPOSE = Path(__file__).resolve().parents[2] / "docker-compose.yml"
FIXED_IN_DOCKER = {
    "DATABASE_URL": "the PostgreSQL container, not the template's SQLite",
    "UPLOAD_DIR": "the uploads volume at /app/uploads",
    "HOST": "the container's command starts uvicorn on 0.0.0.0",
    "PORT": "the container's command starts uvicorn on 8000",
}


def backend_environment():
    return yaml.safe_load(COMPOSE.read_text())["services"]["backend"]["environment"]


def test_every_setting_is_taken_from_env_in_docker():
    environment = backend_environment()

    missing = [
        name for name in Settings.model_fields
        if name not in FIXED_IN_DOCKER and f"${{{name}" not in str(environment.get(name, ""))
    ]

    assert not missing, f"not passed through from .env: {missing}"


def test_the_fixed_ones_are_really_fixed():
    environment = backend_environment()

    assert environment["DATABASE_URL"].startswith("postgresql://") and "@db:" in environment["DATABASE_URL"]
    assert all(name not in environment for name in ("UPLOAD_DIR", "HOST", "PORT"))


def test_docker_defaults_match_the_apps_own():
    environment = backend_environment()

    for name, field in Settings.model_fields.items():
        match = re.fullmatch(r"\$\{" + name + r":-(.*)\}", str(environment.get(name, "")))
        if match and field.default is not None and "${" not in match.group(1):
            assert match.group(1).lower() == str(field.default).lower(), name
