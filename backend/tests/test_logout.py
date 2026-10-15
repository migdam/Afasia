"""Logging out ends that login on the server, not just in the browser (P1-5d)."""
import time

import jwt

from app.core.config import settings

PASSWORD = "correct horse battery"


def sign_up(client, username="pat"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": PASSWORD},
    ).json()


def log_in(client, username="pat"):
    return client.post("/api/v1/auth/login", json={"username": username, "password": PASSWORD}).json()


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_a_token_copied_before_logout_stops_working(client):
    token = sign_up(client)["access_token"]
    client.cookies.clear()

    assert client.post("/api/v1/auth/logout", headers=bearer(token)).status_code == 204

    assert client.get("/api/v1/users/profile", headers=bearer(token)).status_code == 401
    assert client.post("/api/v1/auth/refresh", headers=bearer(token)).status_code == 401


def test_logging_out_through_the_cookie_ends_the_login_too(client):
    token = sign_up(client)["access_token"]
    client.cookies.clear()

    response = client.post(
        "/api/v1/auth/logout", headers={"Cookie": f"access_token={token}", "X-Requested-With": "afasia"},
    )

    assert response.status_code == 204
    assert client.get("/api/v1/users/profile", headers=bearer(token)).status_code == 401


def test_renewed_tokens_of_that_login_end_with_it(client):
    old = sign_up(client)["access_token"]
    client.cookies.clear()
    time.sleep(1)  # so the renewed token differs from the first
    renewed = client.post("/api/v1/auth/refresh", headers=bearer(old)).json()["access_token"]
    client.cookies.clear()

    client.post("/api/v1/auth/logout", headers=bearer(old))

    assert client.get("/api/v1/users/profile", headers=bearer(renewed)).status_code == 401


def test_other_logins_of_the_same_person_carry_on(client):
    phone = sign_up(client)["access_token"]
    laptop = log_in(client)["access_token"]
    client.cookies.clear()

    client.post("/api/v1/auth/logout", headers=bearer(phone))

    assert client.get("/api/v1/users/profile", headers=bearer(laptop)).status_code == 200


def test_tokens_without_a_login_id_are_refused(client):
    user = sign_up(client)["user"]
    client.cookies.clear()
    now = int(time.time())
    token = jwt.encode(
        {"sub": str(user["id"]), "iat": now, "exp": now + 600, "auth_time": now},
        settings.SECRET_KEY, algorithm=settings.ALGORITHM,
    )

    assert client.get("/api/v1/users/profile", headers=bearer(token)).status_code == 401
