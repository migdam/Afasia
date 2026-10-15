"""Logins: password length, limited attempts, and accounts checked on every request."""
from app.db.database import SessionLocal
from app.db.models import User

PASSWORD = "correct horse battery"


def register(client, username, password=PASSWORD):
    return client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": password},
    )


def login(client, username, password=PASSWORD):
    return client.post("/api/v1/auth/login", json={"username": username, "password": password})


def bearer(response):
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_passwords_need_at_least_8_characters(client):
    assert register(client, "pat", "1234567").status_code == 422
    assert register(client, "pat", "12345678").status_code == 201


def test_repeated_wrong_passwords_are_slowed_down(client):
    register(client, "pat")
    register(client, "sam")

    for _ in range(5):
        assert login(client, "pat", "wrong password").status_code == 401
    blocked = login(client, "pat")  # even the right password, for now

    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0
    assert login(client, "sam").status_code == 200  # other accounts are unaffected


def test_a_successful_login_forgets_earlier_mistakes(client):
    register(client, "pat")
    for _ in range(4):
        login(client, "pat", "wrong password")

    assert login(client, "pat").status_code == 200
    for _ in range(4):
        login(client, "pat", "wrong password")
    assert login(client, "pat").status_code == 200


def test_a_deactivated_or_deleted_account_is_logged_out_at_once(client):
    auth = bearer(register(client, "pat"))
    assert client.get("/api/v1/users/profile", headers=auth).status_code == 200

    with SessionLocal() as db:
        db.query(User).filter(User.username == "pat").one().is_active = False
        db.commit()
    assert client.get("/api/v1/users/profile", headers=auth).status_code == 401

    other = bearer(register(client, "sam"))
    with SessionLocal() as db:
        db.delete(db.query(User).filter(User.username == "sam").one())
        db.commit()
    assert client.get("/api/v1/therapy/sessions", headers=other).status_code == 401
