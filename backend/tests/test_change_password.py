"""Changing your password, which also ends your other logins (P1-5e1)."""
import time

PASSWORD = "correct horse battery"
NEW = "a brand new passphrase"


def sign_up(client, username="pat"):
    body = client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": PASSWORD},
    ).json()
    client.cookies.clear()
    return body["access_token"]


def log_in(client, password, username="pat"):
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    client.cookies.clear()
    return response


def change(client, token, current, new):
    response = client.post(
        "/api/v1/users/password", headers={"Authorization": f"Bearer {token}"},
        json={"current_password": current, "new_password": new},
    )
    client.cookies.clear()
    return response


def profile(client, token):
    return client.get("/api/v1/users/profile", headers={"Authorization": f"Bearer {token}"}).status_code


def test_the_new_password_works_and_the_old_one_does_not(client):
    token = sign_up(client)

    assert change(client, token, PASSWORD, NEW).status_code == 200

    assert log_in(client, NEW).status_code == 200
    assert log_in(client, PASSWORD).status_code == 401


def test_other_logins_end_and_this_one_carries_on(client):
    here = sign_up(client)
    elsewhere = log_in(client, PASSWORD).json()["access_token"]
    time.sleep(1)  # logins are timed to the second

    response = change(client, here, PASSWORD, NEW)

    assert profile(client, elsewhere) == 401
    assert profile(client, here) == 401  # the old token of this login too...
    assert profile(client, response.json()["access_token"]) == 200  # ...it gets a new one
    assert "access_token=" in response.headers["set-cookie"]


def test_the_current_password_must_be_right(client):
    token = sign_up(client)

    assert change(client, token, "not my password", NEW).status_code == 400
    assert log_in(client, PASSWORD).status_code == 200


def test_the_new_password_follows_the_sign_up_rules(client):
    token = sign_up(client)

    assert change(client, token, PASSWORD, "short").status_code == 422
    assert change(client, token, PASSWORD, "ą" * 37).status_code == 422  # 74 bytes
    assert log_in(client, PASSWORD).status_code == 200


def test_guessing_the_current_password_is_limited_like_logging_in(client):
    token = sign_up(client)

    for _ in range(5):
        assert change(client, token, "a wrong guess", NEW).status_code == 400
    blocked = change(client, token, PASSWORD, NEW)

    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0
