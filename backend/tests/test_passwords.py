"""Password hashing with bcrypt (passlib, unmaintained, was replaced in P1-4)."""
from app.core.security import get_password_hash, verify_password

PASSWORD = "correct horse battery staple"
# Made by passlib 1.7.4 with bcrypt 4.3.0 before the switch: existing
# accounts must still be able to log in.
PASSLIB_HASH = "$2b$12$SKG5QETcYxWh3FY8SseHLe0SreWYFoQET2q.Km0szGZVXDy2hOhpa"
TOO_LONG = "ą" * 37  # 74 bytes in UTF-8: over bcrypt's 72-byte limit


def test_hashes_made_by_passlib_still_verify():
    assert verify_password(PASSWORD, PASSLIB_HASH)
    assert not verify_password(PASSWORD + "!", PASSLIB_HASH)


def test_new_hashes_verify():
    hashed = get_password_hash(PASSWORD)

    assert hashed.startswith("$2b$")
    assert verify_password(PASSWORD, hashed)
    assert not verify_password(PASSWORD + "!", hashed)


def test_passwords_over_72_bytes_are_refused_not_truncated(client):
    signup = client.post(
        "/api/v1/auth/register",
        json={"email": "pat@example.com", "username": "pat", "password": TOO_LONG},
    )
    assert signup.status_code == 422
    assert "72 bytes" in signup.text

    login = client.post("/api/v1/auth/login", json={"username": "pat", "password": TOO_LONG})
    assert login.status_code == 401
    assert not verify_password(TOO_LONG, PASSLIB_HASH)
