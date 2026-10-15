"""Smoke tests: the backend imports and answers its health check."""
from fastapi.testclient import TestClient

from app.main import app


def test_app_imports():
    assert app.title


def test_health_returns_200():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
