"""Calm feedback after a wrong answer, and a chance to try again (U8, P2-4f)."""
import pytest
from playwright.sync_api import expect
from test_sessions import choose, start_session

TEXT = {
    "en": {"again": "Try again", "right": "That's it."},
    "pl": {"again": "Spróbuj jeszcze raz", "right": "Tak jest."},
}
# Whether a CSS color is reddish: red well above green and blue.
REDDISH = """([selector, property]) => {
    const [r, g, b] = getComputedStyle(document.querySelector(selector))[property].match(/[\\d.]+/g).map(Number);
    return r > g + 40 && r > b + 40;
}"""


def answer_wrongly(page):
    right = choose(page, correct=False)
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_be_visible()
    return right


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_a_wrong_answer_is_not_shown_in_alarm_colors(page, account, theme):
    if theme == "dark":
        page.click("#theme-toggle")
    start_session(page)
    answer_wrongly(page)
    page.wait_for_timeout(400)  # past any color transition

    assert not page.evaluate(REDDISH, ["#feedback", "color"])
    assert not page.evaluate(REDDISH, ["#feedback", "backgroundColor"])


@pytest.mark.parametrize("language", ["en", "pl"])
def test_after_a_wrong_answer_the_person_can_try_again_for_practice(page, account, language):
    if language == "pl":
        page.click("#lang-toggle")
    start_session(page)
    right = answer_wrongly(page)
    again = page.locator("#try-again")
    expect(again).to_have_text(TEXT[language]["again"])

    again.click()
    expect(page.locator("#submit-answer")).to_be_visible()
    page.click(f".option-btn[data-answer='{right}']")
    page.click("#submit-answer")

    expect(page.locator("#feedback")).to_contain_text(TEXT[language]["right"])
    expect(again).to_be_hidden()
    expect(page.locator("#next-exercise")).to_be_visible()


def test_a_right_answer_offers_no_retry_and_the_retry_is_not_scored(page, account):
    start_session(page)
    for number in range(1, 6):
        expect(page.locator("#exercise-counter")).to_have_text(f"{number}/5")
        if number == 1:
            right = answer_wrongly(page)
            page.click("#try-again")
            page.click(f".option-btn[data-answer='{right}']")
            page.click("#submit-answer")
        else:
            choose(page)
            page.click("#submit-answer")
            expect(page.locator("#try-again")).to_be_hidden()
        page.click("#next-exercise")

    # The first answer counts: 4 of 5, practice retry or not.
    expect(page.locator("#app-message")).to_have_text("Session finished. Your score: 80%.")
