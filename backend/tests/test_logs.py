"""Nothing a person types or is given ends up in the server's logs (P1-6f)."""
import logging

from test_recordings import WEBM, an_exercise_of

PASSWORD = "secret horse battery"
NEW_PASSWORD = "another secret passphrase"
EMAIL = "pat.private@example.com"
FULL_NAME = "Patricia Privatename"
ANSWER = "myveryprivateanswer"


def test_a_whole_visit_leaves_no_personal_data_in_the_logs(client, caplog):
    caplog.set_level(logging.DEBUG)  # everything, from every library

    response = client.post("/api/v1/auth/register", json={
        "email": EMAIL, "username": "pat", "password": PASSWORD, "full_name": FULL_NAME,
    })
    token = response.json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}
    client.post("/api/v1/auth/login", json={"username": "pat", "password": "a wrong guess"})
    client.post("/api/v1/auth/login", json={"username": "pat", "password": PASSWORD})
    client.put("/api/v1/users/consents", headers=auth, json={"recordings": True})
    exercise = an_exercise_of(client, auth)
    client.post(f"/api/v1/therapy/exercises/{exercise}/answer", headers=auth,
                json={"answer": ANSWER, "time_taken_seconds": 3})
    client.post(f"/api/v1/users/audio/upload?exercise_id={exercise}", headers=auth,
                files={"audio": ("recording", WEBM, "audio/webm")})
    client.get("/api/v1/users/me/export", headers=auth)
    renewed = client.post("/api/v1/users/password", headers=auth,
                          json={"current_password": PASSWORD, "new_password": NEW_PASSWORD}).json()["access_token"]
    client.request("DELETE", "/api/v1/users/me", headers={"Authorization": f"Bearer {renewed}"},
                   json={"password": NEW_PASSWORD})

    assert caplog.records, "nothing was logged at all, so this test checks nothing"
    logged = caplog.text
    for private in (PASSWORD, NEW_PASSWORD, EMAIL, FULL_NAME, ANSWER, token, renewed):
        assert private not in logged, private
