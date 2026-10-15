"""Smoke tests: the backend imports and answers its health check."""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import InvalidRequestError

# Backlog P0-2: the backend crashes while it is being imported. These tests
# record that. The P0-2 fix removes this marker; because the xfail is strict,
# an unexpected pass fails the run, so the marker can't be forgotten.
crashes_on_import = pytest.mark.xfail(
    raises=(ValidationError, InvalidRequestError, ImportError),
    reason="P0-2: backend crashes at import time",
    strict=True,
)


@crashes_on_import
def test_app_imports():
    from app.main import app

    assert app.title


@crashes_on_import
def test_health_returns_200():
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
