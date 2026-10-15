"""Who may call what (loop/PROMPT.md, G4)."""
import re

import pytest

from app.main import app

PUBLIC = {("POST", "/api/v1/auth/register"), ("POST", "/api/v1/auth/login")}
# Listed from the OpenAPI schema: app.routes doesn't show the routes of
# included routers in every FastAPI version, and an empty list would turn
# these tests into silent skips.
ROUTES = sorted(
    (method.upper(), path)
    for path, operations in app.openapi()["paths"].items()
    if path.startswith("/api/")
    for method in operations
    if (method.upper(), path) not in PUBLIC
)


def test_the_route_list_is_complete():
    assert len(ROUTES) >= 20, ROUTES


def register(client, username):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": "correct horse battery"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.mark.parametrize("method, path", ROUTES, ids=[f"{m} {p}" for m, p in ROUTES])
def test_every_route_but_signing_up_and_in_needs_a_login(client, method, path):
    response = client.request(method, re.sub(r"\{[^}]+\}", "1", path))

    assert response.status_code == 401


ADMIN_ROUTES = [(m, p) for m, p in ROUTES if p.startswith("/api/v1/admin/")]


@pytest.mark.parametrize("method, path", ADMIN_ROUTES, ids=[f"{m} {p}" for m, p in ADMIN_ROUTES])
def test_patients_cannot_use_admin_routes(client, method, path):
    patient = register(client, "pat")

    response = client.request(method, re.sub(r"\{[^}]+\}", "1", path), headers=patient)

    assert response.status_code == 403


def test_users_cannot_see_or_change_each_others_sessions(client):
    pat, sam = register(client, "pat"), register(client, "sam")
    session = client.post(
        "/api/v1/therapy/sessions", headers=pat,
        json={"title": "t", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": 1},
    ).json()
    exercise = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=pat).json()[0]
    plan = client.post(
        "/api/v1/users/scheduled-sessions", headers=pat,
        json={"title": "p", "scheduled_time": "2099-01-01T10:00:00", "exercise_type": "word_naming"},
    ).json()

    assert client.get(f"/api/v1/therapy/sessions/{session['id']}", headers=sam).status_code == 404
    assert client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=sam).status_code == 404
    assert client.post(
        f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=sam,
        json={"answer": "x", "time_taken_seconds": 1},
    ).status_code in (403, 404)
    assert client.post(f"/api/v1/therapy/sessions/{session['id']}/complete", headers=sam).status_code == 404
    assert client.delete(f"/api/v1/users/scheduled-sessions/{plan['id']}", headers=sam).status_code == 404
    assert client.get("/api/v1/therapy/sessions", headers=sam).json() == []
    assert client.get("/api/v1/users/scheduled-sessions", headers=sam).json() == []
    # ...and the owner still has everything.
    assert client.get(f"/api/v1/therapy/sessions/{session['id']}", headers=pat).status_code == 200
    assert len(client.get("/api/v1/users/scheduled-sessions", headers=pat).json()) == 1
