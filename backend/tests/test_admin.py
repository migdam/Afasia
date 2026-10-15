"""Admin endpoints."""
from app.db.database import SessionLocal
from app.db.models import User, UserRole


def register(client, username):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": f"{username}@example.com", "username": username, "password": "correct horse battery"},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def make_admin(username):
    # There is no way to create an admin through the API yet (backlog P1-3).
    with SessionLocal() as db:
        db.query(User).filter(User.username == username).one().role = UserRole.ADMIN
        db.commit()


def test_the_patient_list_says_who_is_active(client):
    register(client, "pat")
    admin = register(client, "ada")
    make_admin("ada")

    users = client.get("/api/v1/admin/users", headers=admin).json()
    assert [(user["username"], user["is_active"]) for user in users] == [("pat", True)]

    client.put(f"/api/v1/admin/users/{users[0]['id']}/deactivate", headers=admin)

    users = client.get("/api/v1/admin/users", headers=admin).json()
    assert users[0]["is_active"] is False
