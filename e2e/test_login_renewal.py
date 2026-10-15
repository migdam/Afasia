"""A login is renewed while the app is in use (P1-5b), through the cookie (P1-5c2)."""
import time
from urllib.parse import urlparse

import jwt
from conftest import PASSWORD, SECRET_KEY, browser_token, call_api
from playwright.sync_api import expect


def test_an_active_user_gets_a_fresh_login_before_the_old_one_runs_out(page, servers, account):
    _, body = call_api(servers, "POST", "/auth/login", {"username": account, "password": PASSWORD})
    now = int(time.time())
    # A login from 20 minutes ago, with 10 minutes left.
    aged = jwt.encode(
        {"sub": str(body["user"]["id"]), "sid": "e2e-aged-login", "iat": now - 1200, "exp": now + 600,
         "auth_time": now - 1200},
        SECRET_KEY, algorithm="HS256",
    )
    page.context.add_cookies([{
        "name": "access_token", "value": aged, "domain": urlparse(servers["api"]).hostname, "path": "/api",
        "httpOnly": True, "secure": True, "sameSite": "Strict",
    }])

    page.reload()  # loading the dashboard uses the API, which counts as activity

    expect(page.locator("#dashboard-page")).to_be_visible()
    deadline = time.monotonic() + 10
    while browser_token(page) == aged and time.monotonic() < deadline:
        page.wait_for_timeout(100)
    fresh = jwt.decode(browser_token(page), SECRET_KEY, algorithms=["HS256"])
    assert fresh["exp"] > now + 600
    assert fresh["auth_time"] == now - 1200


def test_a_fresh_login_is_not_renewed_on_every_call(page, account):
    renewals = []
    page.on("request", lambda request: "/auth/refresh" in request.url and renewals.append(request.url))

    page.click(".nav-item[data-page='progress']")
    expect(page.locator("#progress-total-sessions")).to_have_text("0")
    page.click(".nav-item[data-page='dashboard']")
    page.wait_for_timeout(500)

    assert renewals == []
