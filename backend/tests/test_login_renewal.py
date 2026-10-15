"""Logins are renewed while someone is active, up to a fixed maximum."""
import time

import jwt

from app.core.config import settings

PASSWORD = "correct horse battery"


def sign_up(client, username="pat"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": PASSWORD},
    ).json()


def claims(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def token_for(user_id, logged_in_seconds_ago):
    now = int(time.time())
    return jwt.encode(
        {"sub": str(user_id), "sid": "test-login", "iat": now - 60, "exp": now + 600,
         "auth_time": now - logged_in_seconds_ago},
        settings.SECRET_KEY, algorithm=settings.ALGORITHM,
    )


def refresh(client, token):
    return client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {token}"})


def test_a_login_records_when_it_happened(client):
    token = claims(sign_up(client)["access_token"])

    assert abs(token["auth_time"] - time.time()) < 60
    assert token["iat"] == token["auth_time"]


def test_refreshing_gives_a_later_expiry_and_keeps_the_login_time(client):
    user = sign_up(client)["user"]
    old = token_for(user["id"], logged_in_seconds_ago=3600)

    response = refresh(client, old)

    assert response.status_code == 200
    new = response.json()["access_token"]
    assert claims(new)["exp"] > claims(old)["exp"]
    assert claims(new)["auth_time"] == claims(old)["auth_time"]
    assert client.get("/api/v1/users/profile", headers={"Authorization": f"Bearer {new}"}).status_code == 200


def test_a_login_cannot_be_renewed_past_the_maximum(client):
    user = sign_up(client)["user"]
    limit = settings.LOGIN_MAX_HOURS * 3600

    assert refresh(client, token_for(user["id"], logged_in_seconds_ago=limit + 60)).status_code == 401

    nearly = token_for(user["id"], logged_in_seconds_ago=limit - 120)
    renewed = claims(refresh(client, nearly).json()["access_token"])
    assert renewed["exp"] <= renewed["auth_time"] + limit


def test_tokens_without_a_login_time_are_not_renewed(client):
    user = sign_up(client)["user"]
    now = int(time.time())
    token = jwt.encode({"sub": str(user["id"]), "sid": "test-login", "exp": now + 600}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    assert refresh(client, token).status_code == 401
