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


def from_address(address):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, client=(address, 50000))


def test_someone_elses_wrong_guesses_do_not_lock_you_out(client):
    # People with aphasia may mistype, and a stranger mistyping on purpose
    # must not lock them out too.
    register(client, "pat")
    stranger, patient = from_address("203.0.113.9"), from_address("198.51.100.7")

    for _ in range(5):
        assert login(stranger, "pat", "wrong password").status_code == 401
    assert login(stranger, "pat").status_code == 429

    assert login(patient, "pat").status_code == 200


def test_guessing_from_many_addresses_still_hits_a_limit_for_the_account(client):
    from app.core.config import settings

    register(client, "pat")
    for n in range(settings.LOGIN_MAX_FAILURES_PER_ACCOUNT):
        address = f"10.0.{n // 4}.{n % 4 + 1}"  # 4 tries each, under the per-address limit
        assert login(from_address(address), "pat", "wrong password").status_code == 401

    assert login(from_address("192.0.2.1"), "pat").status_code == 429
