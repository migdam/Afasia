"""The browser talks only to the app and its API: no third parties (P1-6f).

Also: the API server's own log (uvicorn) holds no passwords or emails.
"""
from urllib.parse import urlparse

from conftest import PASSWORD
from playwright.sync_api import expect
from test_full_flow import TEXT, play_session
from test_sessions import record_dialogs


def test_a_whole_visit_requests_nothing_from_other_sites(page, servers, account):
    record_dialogs(page)
    origins = set()
    page.on("request", lambda request: origins.add(urlparse(request.url).netloc))

    play_session(page, "word_naming", TEXT["en"], wrong_first=True)
    page.click(".nav-item[data-page='progress']")
    expect(page.locator("#progress-total-sessions")).to_have_text("1")
    page.click(".nav-item[data-page='account']")
    page.click("#account-page .privacy-link")
    expect(page.locator("section#en h1")).to_be_visible()

    allowed = {urlparse(servers["web"]).netloc, urlparse(servers["api"]).netloc}
    assert origins and origins <= allowed, origins - allowed


def test_the_api_log_holds_no_passwords_or_emails(page, servers, account):
    log = (servers["db"].parent / "api.log").read_text()

    assert "POST /api/v1/auth/register" in log  # it is the right log, and it logs requests
    assert PASSWORD not in log
    assert f"{account}@example.com" not in log
