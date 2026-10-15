"""Text that people typed is shown as text, never run as page markup (P1-1)."""
from conftest import browser_token, call_api
from playwright.sync_api import expect

MARKUP = "<b>bold</b><img src=x onerror=alert(1)>"


def test_titles_with_markup_are_shown_as_text(page, servers, account):
    dialogs = []
    page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
    token = browser_token(page)
    status, _ = call_api(
        servers, "POST", "/therapy/sessions",
        {"title": MARKUP, "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": 5}, token,
    )
    assert status == 200
    status, _ = call_api(
        servers, "POST", "/users/scheduled-sessions",
        {"title": MARKUP, "scheduled_time": "2099-01-01T10:00:00", "exercise_type": "word_naming", "difficulty": "easy"},
        token,
    )
    assert status == 200

    page.reload()

    expect(page.locator("#recent-sessions .session-title")).to_have_text(MARKUP)
    expect(page.locator("#scheduled-list .session-title")).to_have_text(MARKUP)
    assert page.locator("#dashboard-page img, #dashboard-page b").count() == 0
    assert dialogs == []


def test_the_page_forbids_inline_scripts(page):
    policy = page.locator("meta[http-equiv='Content-Security-Policy']").get_attribute("content")

    script_src = next(part for part in policy.split(";") if part.strip().startswith("script-src"))
    assert script_src.split() == ["script-src", "'self'"]
