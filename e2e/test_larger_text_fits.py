"""On a phone, with larger text and in either language, nothing spills out
of its box and no screen scrolls sideways (U1, U5; backlog P2-12)."""
import uuid

import pytest
from playwright.sync_api import expect

from conftest import PASSWORD, browser_token, call_api
from test_admin import make_admin
from test_session_lists_fit import PHONE, finish

# Elements whose content is wider than they are (text spilling out of a
# button, say), or that reach past the screen's edge.
SPILLS = """() => {
    const found = [];
    if (document.documentElement.scrollWidth > window.innerWidth + 1) {
        found.push(`the page scrolls sideways (${document.documentElement.scrollWidth} px)`);
    }
    for (const node of document.querySelectorAll('body *')) {
        if (!node.checkVisibility() || node.tagName === 'CANVAS') continue;
        const name = `${node.tagName.toLowerCase()}.${[...node.classList].join('.')} "${node.textContent.trim().slice(0, 30)}"`;
        const scrolls = ['auto', 'scroll', 'hidden', 'clip'].includes(getComputedStyle(node).overflowX);
        if (!scrolls && node.clientWidth > 0 && node.scrollWidth > node.clientWidth + 1) {
            found.push(`${name} is ${node.scrollWidth} px wide inside ${node.clientWidth} px`);
        }
        if (node.getBoundingClientRect().right > window.innerWidth + 1) {
            found.push(`${name} reaches past the screen`);
        }
    }
    return found;
}"""


def spills(page, screen):
    page.mouse.move(1, 300)  # off the buttons: a hovered button grows a little
    return [f"{screen}: {problem}" for problem in page.evaluate(SPILLS)]


def sign_up(page):
    username = f"pat{uuid.uuid4().hex[:8]}"
    page.click("#show-register")
    page.fill("#register-email", f"{username}@example.com")
    page.fill("#register-username", username)
    page.fill("#register-password", PASSWORD)
    page.click("#register-form-submit button[type=submit]")
    expect(page.locator("#dashboard-page")).to_be_visible()
    return username


def start(page, exercise_type):
    page.select_option("#exercise-type", exercise_type)
    page.click("#new-session-form button[type=submit]")
    expect(page.locator("#exercise-counter")).to_be_visible()


@pytest.mark.parametrize("polish, larger", [(True, True), (False, True), (True, False)],
                         ids=["pl-larger", "en-larger", "pl"])
def test_every_screen_fits_a_phone(page, servers, polish, larger):
    page.set_viewport_size(PHONE)
    if polish:
        page.click("#lang-toggle")
    if larger:
        page.click("#text-size")
    found = spills(page, "login")
    page.click("#show-register")
    found += spills(page, "sign-up")
    page.click("#show-login")

    username = sign_up(page)
    token = browser_token(page)
    finish(servers, token, "pronunciation", "medium", "said_it")
    call_api(servers, "POST", "/users/scheduled-sessions", {
        "title": "Ćwiczenia z nazw przedmiotów codziennego użytku", "scheduled_time": "2099-01-01T10:00:00",
        "exercise_type": "sentence_completion", "difficulty": "medium",
    }, token)
    patient = f"pat{uuid.uuid4().hex[:8]}"  # someone for the admin list
    call_api(servers, "POST", "/auth/register",
             {"email": f"{patient}@example.com", "username": patient, "password": PASSWORD})
    make_admin(servers, username)
    page.reload()
    expect(page.locator("#recent-sessions .session-item")).to_have_count(1)
    expect(page.locator("#scheduled-list .session-item")).to_have_count(1)
    found += spills(page, "dashboard")

    page.click(".bottom-nav [data-page='progress']")
    expect(page.locator(".badge-item")).to_have_count(1)
    found += spills(page, "progress")
    page.click(".bottom-nav [data-page='account']")
    expect(page.locator("#account-page")).to_be_visible()
    found += spills(page, "account")
    page.click(".bottom-nav [data-page='admin']")
    expect(page.locator(".user-item").first).to_be_visible()
    found += spills(page, "admin")

    page.click(".bottom-nav [data-page='dashboard']")
    start(page, "word_naming")
    page.click("#hint-btn")
    found += spills(page, "naming with a hint")
    page.fill("#answer-input", "zzz")
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_be_visible()
    found += spills(page, "feedback")
    page.click("#exit-exercise")
    found += spills(page, "leave dialog")
    page.click("#leave-go")
    for exercise_type in ("sentence_completion", "pronunciation"):
        start(page, exercise_type)
        found += spills(page, exercise_type)
        page.click("#exit-exercise")
        page.click("#leave-go")

    assert found == []
