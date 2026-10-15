"""Signing up, staying signed in, and logging back in, in a real browser."""
import uuid

from playwright.sync_api import expect

PASSWORD = "correct horse battery staple"


def sign_up(page):
    username = f"pat{uuid.uuid4().hex[:8]}"
    page.click("#show-register")
    page.fill("#register-email", f"{username}@example.com")
    page.fill("#register-username", username)
    page.fill("#register-password", PASSWORD)
    page.click("#register-form-submit button[type=submit]")
    expect(page.locator("#dashboard-page")).to_be_visible()
    return username


def test_signing_up_opens_the_dashboard_and_survives_a_reload(page):
    sign_up(page)
    expect(page.locator("#total-points")).to_have_text("0")

    page.reload()  # the stored token must still be accepted (P0-3)

    expect(page.locator("#dashboard-page")).to_be_visible()
    expect(page.locator("#logout-btn")).to_be_visible()


def test_logging_out_shows_an_empty_login_form(page):
    username = sign_up(page)

    page.click("#logout-btn")

    expect(page.locator("#auth-page")).to_be_visible()
    expect(page.locator("#login-form")).to_be_visible()
    expect(page.locator("#register-password")).to_have_value("")

    page.fill("#login-username", username)
    page.fill("#login-password", PASSWORD)
    page.click("#login-form-submit button[type=submit]")

    expect(page.locator("#dashboard-page")).to_be_visible()
