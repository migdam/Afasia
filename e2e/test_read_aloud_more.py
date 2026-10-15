"""Read aloud for messages and instructions beyond the exercise (P2-4d2, U3)."""
import json

from playwright.sync_api import expect
from test_read_aloud import FAKE_SPEECH, LOCAL, spoken, with_voices
from test_sessions import start_session


def with_voices_login(page):
    """The fake speech engine, on the login page (no account)."""
    page.add_init_script(FAKE_SPEECH % json.dumps(LOCAL))
    page.reload()
    expect(page.locator("#auth-page")).to_be_visible()


def read_button_for(page, target):
    return page.locator(f"{target} + .read-aloud")


def test_a_login_message_can_be_read_and_has_no_button_while_empty(page):
    with_voices_login(page)
    button = read_button_for(page, "#login-message")
    expect(button).to_be_hidden()

    page.fill("#login-username", "nobody")
    page.fill("#login-password", "not a password")
    page.click("#login-form-submit button[type=submit]")
    expect(button).to_be_visible()
    button.click()

    assert spoken(page)[-1]["text"] == page.inner_text("#login-message")


def test_the_consent_question_can_be_read_in_polish(page, account):
    with_voices(page, LOCAL)
    page.click("#lang-toggle")
    start_session(page, "pronunciation")
    page.click("#record-btn")
    expect(page.locator("#consent-dialog")).to_be_visible()

    read_button_for(page, "#consent-text").click()

    said = spoken(page)[-1]
    assert said["text"] == page.inner_text("#consent-text")
    assert said["voice"] == "Local PL"
    page.click("#consent-no")


def test_the_leave_question_and_the_result_message_can_be_read(page, account):
    with_voices(page, LOCAL)
    start_session(page)
    page.click("#exit-exercise")
    read_button_for(page, "#leave-text").click()
    assert spoken(page)[-1]["text"] == page.inner_text("#leave-text")
    page.click("#leave-stay")

    for number in range(1, 6):
        expect(page.locator("#exercise-counter")).to_have_text(f"{number}/5")
        page.locator(".option-btn").first.click()
        page.click("#submit-answer")
        page.click("#next-exercise")
    expect(page.locator("#app-message")).to_be_visible()
    read_button_for(page, "#app-message").click()

    assert spoken(page)[-1]["text"].startswith("Session finished.")


def test_the_your_data_explanation_can_be_read(page, account):
    with_voices(page, LOCAL)
    page.click(".nav-item[data-page='account']")

    read_button_for(page, "#data-text").click()

    assert spoken(page)[-1]["text"] == page.inner_text("#data-text")
