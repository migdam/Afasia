"""No time pressure (U4, WCAG 2.2.1): no visible clock, and the app waits
for the person to move on (P2-4a)."""
import pytest
from playwright.sync_api import expect
from test_sessions import choose, start_session

LABEL = {"en": {"next": "Next", "last": "See my result"}, "pl": {"next": "Dalej", "last": "Zobacz wynik"}}


def test_no_clock_is_shown(page, account):
    start_session(page)

    expect(page.locator("#exercise-timer")).to_have_count(0)


@pytest.mark.parametrize("language", ["en", "pl"])
def test_the_exercise_waits_until_the_person_moves_on(page, account, language):
    if language == "pl":
        page.click("#lang-toggle")
    start_session(page)
    choose(page)
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_be_visible()

    page.wait_for_timeout(3000)  # longer than the old automatic 2 seconds

    expect(page.locator("#exercise-counter")).to_have_text("1/5")
    next_button = page.locator("#next-exercise")
    expect(next_button).to_have_text(LABEL[language]["next"])
    expect(next_button).to_be_focused()
    expect(page.locator("#submit-answer")).to_be_hidden()
    next_button.click()
    expect(page.locator("#exercise-counter")).to_have_text("2/5")
    expect(next_button).to_be_hidden()


def test_after_the_last_exercise_the_button_shows_the_result(page, account):
    start_session(page)
    for number in range(1, 6):
        expect(page.locator("#exercise-counter")).to_have_text(f"{number}/5")
        choose(page)
        page.click("#submit-answer")
        if number < 5:
            page.click("#next-exercise")

    expect(page.locator("#next-exercise")).to_have_text(LABEL["en"]["last"])
    page.click("#next-exercise")
    expect(page.locator("#dashboard-page")).to_be_visible()
