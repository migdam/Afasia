"""Signing up, staying signed in, and logging back in, in a real browser."""
from conftest import PASSWORD, browser_token, call_api, login_cookie
from playwright.sync_api import expect


def test_signing_up_opens_the_dashboard_and_survives_a_reload(page, account):
    expect(page.locator("#total-points")).to_have_text("0")

    page.reload()  # the stored token must still be accepted (P0-3)

    expect(page.locator("#dashboard-page")).to_be_visible()
    expect(page.locator("#logout-btn")).to_be_visible()


def test_logging_out_shows_an_empty_login_form(page, account):
    page.click("#logout-btn")

    expect(page.locator("#auth-page")).to_be_visible()
    expect(page.locator("#login-form")).to_be_visible()
    expect(page.locator("#register-password")).to_have_value("")

    page.fill("#login-username", account)
    page.fill("#login-password", PASSWORD)
    page.click("#login-form-submit button[type=submit]")

    expect(page.locator("#dashboard-page")).to_be_visible()


def test_the_login_is_kept_where_page_scripts_cannot_read_it(page, account):
    cookie = login_cookie(page)

    assert cookie["httpOnly"] and cookie["secure"] and cookie["sameSite"] == "Strict"
    assert "access_token" not in page.evaluate("document.cookie")
    assert page.evaluate("localStorage.getItem('access_token')") is None


def test_a_token_left_by_an_older_version_is_removed(page, account):
    page.evaluate("localStorage.setItem('access_token', 'old')")

    page.reload()

    expect(page.locator("#dashboard-page")).to_be_visible()
    assert page.evaluate("localStorage.getItem('access_token')") is None


def test_logging_out_ends_the_login_for_good(page, servers, account):
    token = browser_token(page)

    page.click("#logout-btn")
    expect(page.locator("#auth-page")).to_be_visible()

    assert login_cookie(page) is None
    status, _ = call_api(servers, "GET", "/users/profile", token=token)
    assert status == 401  # a copy of the token is no use either (P1-5d)
    page.reload()
    expect(page.locator("#auth-page")).to_be_visible()
    expect(page.locator("#dashboard-page")).to_be_hidden()
