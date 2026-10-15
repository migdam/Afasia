"""The admin command line: creating staff accounts and changing roles."""
import io

from app import cli

PASSWORD = "a long staff password"


def run(monkeypatch, *args, stdin=""):
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    return cli.main(list(args))


def login(client, username, password=PASSWORD):
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    return {"Authorization": f"Bearer {response.json()['access_token']}"} if response.status_code == 200 else None


def test_create_user_makes_a_staff_account_that_can_log_in(client, monkeypatch):
    code = run(
        monkeypatch, "create-user", "--username", "ada", "--email", "ada@example.com",
        "--role", "admin", "--password-stdin", stdin=PASSWORD + "\n",
    )

    assert code == 0
    admin = login(client, "ada")
    assert client.get("/api/v1/admin/stats", headers=admin).status_code == 200
    assert client.get("/api/v1/users/profile", headers=admin).json()["role"] == "admin"


def test_set_role_promotes_an_existing_account(client, monkeypatch):
    client.post(
        "/api/v1/auth/register",
        json={"email": "tess@example.com", "username": "tess", "password": PASSWORD},
    )
    assert client.get("/api/v1/admin/stats", headers=login(client, "tess")).status_code == 403

    assert run(monkeypatch, "set-role", "tess", "therapist") == 0

    assert client.get("/api/v1/admin/stats", headers=login(client, "tess")).status_code == 200


def test_mistakes_are_refused_with_a_message(client, monkeypatch, capsys):
    assert run(monkeypatch, "set-role", "nobody", "admin") == 1
    assert "no user called nobody" in capsys.readouterr().err

    assert run(
        monkeypatch, "create-user", "--username", "ada", "--email", "ada@example.com",
        "--role", "admin", "--password-stdin", stdin="short\n",
    ) == 1
    assert "at least" in capsys.readouterr().err

    run(monkeypatch, "create-user", "--username", "ada", "--email", "ada@example.com",
        "--role", "admin", "--password-stdin", stdin=PASSWORD + "\n")
    assert run(
        monkeypatch, "create-user", "--username", "ada", "--email", "other@example.com",
        "--role", "admin", "--password-stdin", stdin=PASSWORD + "\n",
    ) == 1
    assert "already" in capsys.readouterr().err
