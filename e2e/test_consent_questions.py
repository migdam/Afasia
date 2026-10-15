"""The app asks before recording and before speech recognition (P1-6b2)."""
import pytest
from conftest import browser_token, call_api
from playwright.sync_api import expect
from test_microphone import COUNT_STREAMS, RECORDING
from test_sessions import start_session

# A stand-in for the browser's speech recognition that counts its starts.
FAKE_RECOGNITION = """
window.__recognitionStarts = 0;
class FakeRecognition {
    start() {
        window.__recognitionStarts++;
        setTimeout(() => this.onresult({ results: [[{ transcript: 'hello', confidence: 0.9 }]] }), 10);
    }
    stop() {}
}
window.SpeechRecognition = FakeRecognition;
window.webkitSpeechRecognition = FakeRecognition;
"""
TEXT = {
    "en": {"title": "Keep your recordings?", "off": "Recording is off"},
    "pl": {"title": "Przechowywać Twoje nagrania?", "off": "Nagrywanie jest wyłączone"},
}


def consents(page, servers):
    return call_api(servers, "GET", "/users/consents", token=browser_token(page))[1]


def open_pronunciation(page, language="en", servers=None, **given):
    if given:
        call_api(servers, "PUT", "/users/consents", given, token=browser_token(page))
    page.add_init_script(COUNT_STREAMS)
    page.add_init_script(FAKE_RECOGNITION)
    page.reload()
    expect(page.locator("#dashboard-page")).to_be_visible()
    if language == "pl":
        page.click("#lang-toggle")
    start_session(page, "pronunciation")


def streams_opened(page):
    return page.evaluate("window.__micStreams.length")


@pytest.mark.parametrize("language", ["en", "pl"])
def test_the_first_recording_asks_and_no_keeps_the_microphone_off(page, servers, account, language):
    open_pronunciation(page, language)

    page.click("#record-btn")
    dialog = page.locator("#consent-dialog")
    expect(dialog).to_be_visible()
    expect(dialog).to_contain_text(TEXT[language]["title"])
    page.click("#consent-no")

    expect(dialog).to_be_hidden()
    expect(page.locator("#recording-status")).to_contain_text(TEXT[language]["off"])
    assert streams_opened(page) == 0
    assert consents(page, servers)["recordings"] is False


def test_yes_starts_the_recording_and_is_not_asked_again(page, servers, account):
    open_pronunciation(page)

    page.click("#record-btn")
    page.click("#consent-yes")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    page.click("#record-btn")
    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)

    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    expect(page.locator("#consent-dialog")).to_be_hidden()
    assert consents(page, servers)["recordings"] is True


def test_the_answers_can_be_changed_on_the_account_page(page, servers, account):
    call_api(servers, "PUT", "/users/consents", {"recordings": True}, token=browser_token(page))
    page.click(".nav-item[data-page='account']")
    box = page.locator("#consent-recordings")
    expect(box).to_be_checked()
    expect(page.locator("#consent-speech")).not_to_be_checked()

    box.uncheck()

    expect(page.locator("#consent-message")).to_have_text("Saved.")
    assert consents(page, servers)["recordings"] is False


def test_speech_recognition_is_asked_about_separately(page, servers, account):
    open_pronunciation(page, servers=servers, recordings=True)
    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    page.click("#record-btn")
    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)

    page.click("#submit-answer")
    expect(page.locator("#consent-dialog")).to_contain_text("speech recognition")
    page.click("#consent-no")

    expect(page.locator("#feedback")).to_be_visible()
    assert page.evaluate("window.__recognitionStarts") == 0
    assert consents(page, servers)["speech_recognition"] is False


def test_with_consent_speech_recognition_is_used(page, servers, account):
    open_pronunciation(page, servers=servers, recordings=True, speech_recognition=True)
    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    page.click("#record-btn")
    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)

    page.click("#submit-answer")

    expect(page.locator("#feedback")).to_be_visible()
    expect(page.locator("#consent-dialog")).to_be_hidden()
    assert page.evaluate("window.__recognitionStarts") == 1
