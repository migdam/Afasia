"""In Polish, no screen shows English (G9, backlog P2-10a)."""
import re
import uuid

from playwright.sync_api import expect

from conftest import PASSWORD, browser_token, call_api
from test_admin import make_admin
from test_microphone import RECORDING
from test_speech_practice import open_pronunciation

# Words of the English texts that no Polish text uses.
ENGLISH = re.compile(
    r"\b(the|and|your|you|click|points|completed|activate|deactivate|recording|session|"
    r"streak|easy|medium|hard|type|answer|change|toggle|dark|mode|language|first|stop|"
    r"therapy|picture|audio|no data)\b",
    re.I,
)

# Every visible text, and the labels, placeholders and titles a screen
# reader or the eye may meet, with the page's own title.
TEXTS = """() => {
    const seen = [document.title];
    for (const node of document.querySelectorAll('body *')) {
        if (!node.checkVisibility()) continue;
        for (const child of node.childNodes) {
            if (child.nodeType === Node.TEXT_NODE && child.textContent.trim()) seen.push(child.textContent.trim());
        }
        for (const name of ['aria-label', 'placeholder', 'title', 'alt']) {
            if (node.getAttribute(name)) seen.push(node.getAttribute(name));
        }
    }
    return seen;
}"""


def english_on(page):
    return sorted({text for text in page.evaluate(TEXTS) if ENGLISH.search(text)})


def finish_a_session(servers, token):
    _, session = call_api(servers, "POST", "/therapy/sessions", {
        "title": "pronunciation - easy", "exercise_type": "pronunciation", "difficulty": "easy",
        "num_exercises": 1, "language": "pl",
    }, token)
    _, exercises = call_api(servers, "GET", f"/therapy/sessions/{session['id']}/exercises", token=token)
    call_api(servers, "POST", f"/therapy/exercises/{exercises[0]['id']}/answer",
             {"answer": "", "time_taken_seconds": 3, "self_rating": "said_it"}, token)


def go_to(page, name):
    page.click(f".bottom-nav [data-page='{name}']")
    expect(page.locator(f"#{name}-page")).to_be_visible()


def test_no_screen_shows_english_in_polish(page, servers):
    page.click("#lang-toggle")  # Polski, before logging in
    assert english_on(page) == []

    username = f"pat{uuid.uuid4().hex[:8]}"
    page.click("#show-register")
    assert english_on(page) == []
    page.fill("#register-email", f"{username}@example.com")
    page.fill("#register-username", username)
    page.fill("#register-password", PASSWORD)
    page.click("#register-form-submit button[type=submit]")
    expect(page.locator("#dashboard-page")).to_be_visible()

    finish_a_session(servers, browser_token(page))  # a finished session, and a badge
    patient = f"pat{uuid.uuid4().hex[:8]}"  # someone for the admin list
    call_api(servers, "POST", "/auth/register",
             {"email": f"{patient}@example.com", "username": patient, "password": PASSWORD})
    make_admin(servers, username)
    page.reload()
    expect(page.locator("#recent-sessions .session-item")).to_have_count(1)
    assert english_on(page) == []

    go_to(page, "progress")
    expect(page.locator(".badge-item")).to_have_count(1)
    assert english_on(page) == []
    go_to(page, "account")
    assert english_on(page) == []
    go_to(page, "admin")
    expect(page.locator(".user-item").first).to_be_visible()  # the first 50 patients
    assert english_on(page) == []

    go_to(page, "dashboard")
    page.select_option("#exercise-type", "word_naming")
    page.click("#new-session-form button[type=submit]")
    expect(page.locator("#exercise-counter")).to_be_visible()
    assert english_on(page) == []


def test_recording_speaks_polish_too(page, servers, account):
    open_pronunciation(page, servers, recordings=True, speech_recognition=False)  # in Polish

    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    expect(page.locator("#record-btn")).to_contain_text("Zatrzymaj")
    expect(page.locator("#recording-status")).to_have_text("Nagrywanie…")
    assert english_on(page) == []

    page.click("#record-btn")
    expect(page.locator("#recording-status")).to_have_text(
        "Nagranie gotowe. Odsłuchaj je, a potem wybierz, jak poszło.")
    assert english_on(page) == []
