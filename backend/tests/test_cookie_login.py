"""Browser logins travel in an httpOnly cookie that page scripts can't read (P1-5c1)."""
PASSWORD = "correct horse battery"
SESSION = {"title": "t", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": 1}


def sign_up(client, username="pat"):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": PASSWORD},
    )
    client.cookies.clear()  # each test sends the cookie by hand
    return response


def cookie_from(response):
    header = response.headers["set-cookie"]
    return header, header.split(";")[0]  # ("access_token=...; HttpOnly; ...", "access_token=...")


def test_signing_up_and_logging_in_set_a_cookie_scripts_cannot_read(client):
    for response in (
        sign_up(client),
        client.post("/api/v1/auth/login", json={"username": "pat", "password": PASSWORD}),
    ):
        header, _ = cookie_from(response)
        attributes = [part.strip().lower() for part in header.split(";")]
        assert header.startswith("access_token=")
        assert {"httponly", "secure", "samesite=strict", "path=/api"} <= set(attributes)


def test_the_cookie_alone_is_enough_to_read(client):
    _, cookie = cookie_from(sign_up(client))

    response = client.get("/api/v1/users/profile", headers={"Cookie": cookie})

    assert response.status_code == 200
    assert response.json()["username"] == "pat"


def test_changes_through_the_cookie_need_the_apps_own_header(client):
    # Another site can make a browser send the cookie, but it can't add a
    # custom header without passing CORS, which only allows our own origins.
    _, cookie = cookie_from(sign_up(client))

    forged = client.post("/api/v1/therapy/sessions", headers={"Cookie": cookie}, json=SESSION)
    genuine = client.post(
        "/api/v1/therapy/sessions", headers={"Cookie": cookie, "X-Requested-With": "afasia"}, json=SESSION,
    )

    assert forged.status_code == 403
    assert genuine.status_code == 200


def test_bearer_tokens_still_work_for_other_clients(client):
    token = sign_up(client).json()["access_token"]

    response = client.post("/api/v1/therapy/sessions", headers={"Authorization": f"Bearer {token}"}, json=SESSION)

    assert response.status_code == 200


def test_renewing_through_the_cookie_sets_a_new_cookie(client):
    _, cookie = cookie_from(sign_up(client))

    response = client.post("/api/v1/auth/refresh", headers={"Cookie": cookie, "X-Requested-With": "afasia"})

    assert response.status_code == 200
    assert cookie_from(response)[0].startswith("access_token=")


def test_logging_out_removes_the_cookie(client):
    sign_up(client)

    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 204
    header = response.headers["set-cookie"].lower()
    assert header.startswith('access_token=""') or header.startswith("access_token=;")
    assert "max-age=0" in header
