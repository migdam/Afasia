"""A login is renewed while the app is in use (P1-5b)."""
import time

import jwt
from conftest import PASSWORD, SECRET_KEY, call_api
from playwright.sync_api import expect


def stored_token(page):
    return page.evaluate("localStorage.getItem('access_token')")


def test_an_active_user_gets_a_fresh_token_before_the_old_one_runs_out(page, servers, account):
    _, body = call_api(servers, "POST", "/auth/login", {"username": account, "password": PASSWORD})
    now = int(time.time())
    # A login from 20 minutes ago, with 10 minutes left.
    aged = jwt.encode(
        {"sub": str(body["user"]["id"]), "iat": now - 1200, "exp": now + 600, "auth_time": now - 1200},
        SECRET_KEY, algorithm="HS256",
    )
    page.evaluate("token => localStorage.setItem('access_token', token)", aged)

    page.reload()  # loading the dashboard uses the API, which counts as activity

    expect(page.locator("#dashboard-page")).to_be_visible()
    page.wait_for_function("old => localStorage.getItem('access_token') !== old", arg=aged)
    fresh = jwt.decode(stored_token(page), SECRET_KEY, algorithms=["HS256"])
    assert fresh["exp"] > now + 600
    assert fresh["auth_time"] == now - 1200


def test_a_fresh_token_is_left_alone(page, account):
    token = stored_token(page)

    page.reload()
    expect(page.locator("#dashboard-page")).to_be_visible()
    page.wait_for_timeout(1000)

    assert stored_token(page) == token
