"""The admin page: patients are listed as plain text and can be deactivated."""
import sqlite3
import uuid

from conftest import PASSWORD, call_api
from playwright.sync_api import expect


def make_admin(servers, username):
    # There is no way to create an admin through the app yet (backlog P1-3).
    # SQLAlchemy stores enum names, so the role is 'ADMIN'.
    with sqlite3.connect(servers["db"]) as db:
        db.execute("UPDATE users SET role = 'ADMIN' WHERE username = ?", (username,))


def test_an_admin_sees_patients_as_text_and_can_deactivate_them(page, servers, account):
    name = f"pat{uuid.uuid4().hex[:6]}"
    username = f"<b>{name}</b>"  # markup in a username must not be rendered
    status, _ = call_api(
        servers, "POST", "/auth/register",
        {"email": f"{name}@example.com", "username": username, "password": PASSWORD},
    )
    assert status == 201
    make_admin(servers, account)
    page.reload()

    page.click("#admin-nav")

    row = page.locator(".user-item", has_text=name)
    expect(row.locator("h4")).to_have_text(username)
    row.get_by_role("button", name="Deactivate").click()

    expect(row.get_by_role("button", name="Activate")).to_be_visible()
    status, body = call_api(servers, "POST", "/auth/login", {"username": username, "password": PASSWORD})
    assert (status, body["detail"]) == (400, "Inactive user")


def test_the_admin_menu_is_gone_for_the_next_person_to_log_in(page, servers, account):
    patient = f"pat{uuid.uuid4().hex[:6]}"
    status, _ = call_api(
        servers, "POST", "/auth/register",
        {"email": f"{patient}@example.com", "username": patient, "password": PASSWORD},
    )
    assert status == 201
    make_admin(servers, account)
    page.reload()
    expect(page.locator("#admin-nav")).to_be_visible()

    page.click("#logout-btn")
    page.fill("#login-username", patient)
    page.fill("#login-password", PASSWORD)
    page.click("#login-form-submit button[type=submit]")

    expect(page.locator("#dashboard-page")).to_be_visible()
    expect(page.locator("#admin-nav")).to_be_hidden()
