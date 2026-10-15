"""Authentication: tokens from register and login work; anything else gets 401."""
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import get_password_hash, verify_password

PASSWORD = "correct horse battery staple"
PROFILE = "/api/v1/users/profile"
IN_AN_HOUR = datetime.now(timezone.utc) + timedelta(hours=1)
AN_HOUR_AGO = datetime.now(timezone.utc) - timedelta(hours=1)


def register(client, username="alice"):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": PASSWORD},
    )
    assert response.status_code == 201, response.text
    return response.json()


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_password_hashes_verify():
    hashed = get_password_hash(PASSWORD)

    assert hashed != PASSWORD
    assert verify_password(PASSWORD, hashed)
    assert not verify_password(PASSWORD + "!", hashed)


def test_tokens_from_register_and_login_open_the_profile(client):
    registered = register(client)
    login = client.post("/api/v1/auth/login", json={"username": "alice", "password": PASSWORD})
    assert login.status_code == 200, login.text

    for token in (registered["access_token"], login.json()["access_token"]):
        response = client.get(PROFILE, headers=bearer(token))
        assert response.status_code == 200, response.text
        assert response.json()["username"] == "alice"


@pytest.mark.parametrize(
    "headers",
    [{}, bearer("not-a-jwt"), {"Authorization": "Basic YWxpY2U6c2VjcmV0"}],
    ids=["no-header", "not-a-jwt", "basic-auth"],
)
def test_requests_without_a_valid_bearer_token_get_401(client, headers):
    response = client.get(PROFILE, headers=headers)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "claims, key",
    [
        ({"sub": "1", "exp": IN_AN_HOUR}, "a-different-key-that-is-32-bytes!"),
        ({"sub": "1", "exp": AN_HOUR_AGO}, None),
        ({"sub": "1"}, None),
        ({"exp": IN_AN_HOUR}, None),
        ({"sub": "alice", "exp": IN_AN_HOUR}, None),
    ],
    ids=["wrong-key", "expired", "no-expiry", "no-subject", "subject-not-an-id"],
)
def test_tokens_that_fail_validation_get_401(client, claims, key):
    register(client)  # user 1 exists, so a 401 can't come from a missing user
    token = jwt.encode(claims, key or settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    response = client.get(PROFILE, headers=bearer(token))

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_unsigned_tokens_get_401(client):
    register(client)
    token = jwt.encode({"sub": "1", "exp": IN_AN_HOUR}, None, algorithm="none")

    response = client.get(PROFILE, headers=bearer(token))

    assert response.status_code == 401
