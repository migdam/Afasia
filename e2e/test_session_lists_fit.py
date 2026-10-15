"""Session lists fit a phone screen: no score, badge or button is cut off,
in either language or text size (backlog P1-11)."""
import pytest
from playwright.sync_api import expect

from conftest import browser_token, call_api

PHONE = {"width": 390, "height": 844}

# The parts of each session card that stick out of it, by their text.
STICKING_OUT = """() => [...document.querySelectorAll('.session-item')].flatMap((item) => {
    const card = item.getBoundingClientRect();
    const parts = [...item.querySelectorAll('.session-title, .session-meta > *, .session-score, button')];
    const out = parts.filter((part) => {
        const box = part.getBoundingClientRect();
        return box.left < card.left - 0.5 || box.right > card.right + 0.5;
    }).map((part) => part.textContent.trim());
    return item.scrollWidth > item.clientWidth ? [...out, 'the card scrolls'] : out;
})"""


def finish(servers, token, exercise_type, difficulty, rating):
    _, session = call_api(servers, "POST", "/therapy/sessions", {
        "title": f"{exercise_type} - {difficulty}", "exercise_type": exercise_type,
        "difficulty": difficulty, "num_exercises": 1,
    }, token)
    _, exercises = call_api(servers, "GET", f"/therapy/sessions/{session['id']}/exercises", token=token)
    call_api(servers, "POST", f"/therapy/exercises/{exercises[0]['id']}/answer",
             {"answer": "", "time_taken_seconds": 3, "self_rating": rating}, token)


@pytest.mark.parametrize("polish", [False, True], ids=["en", "pl"])
@pytest.mark.parametrize("larger", [False, True], ids=["text", "larger-text"])
def test_session_cards_fit_a_phone(page, servers, account, polish, larger):
    token = browser_token(page)
    finish(servers, token, "pronunciation", "medium", "said_it")  # 100%
    finish(servers, token, "pronunciation", "hard", "not_yet")    # 0%
    call_api(servers, "POST", "/users/scheduled-sessions", {
        "title": "Practising the names of everyday things", "scheduled_time": "2099-01-01T10:00:00",
        "exercise_type": "sentence_completion", "difficulty": "medium",
    }, token)
    page.set_viewport_size(PHONE)
    if polish:
        page.click("#lang-toggle")
    if larger:
        page.click("#text-size")
    page.reload()

    expect(page.locator("#recent-sessions .session-score")).to_have_count(2)
    expect(page.locator("#scheduled-list .session-item")).to_have_count(1)
    assert page.evaluate(STICKING_OUT) == []
    rights = page.evaluate("() => [...document.querySelectorAll('.session-score')].map((s) => s.getBoundingClientRect().right)")
    assert all(right <= PHONE["width"] for right in rights), rights  # on the screen, not past its edge
