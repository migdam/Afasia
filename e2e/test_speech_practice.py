"""Speech practice that works (C5, P2-7a): listen, record, play back,
rate yourself; speech recognition only suggests, during the recording."""
from conftest import browser_token, call_api
from playwright.sync_api import expect
from test_consent_questions import FAKE_RECOGNITION
from test_microphone import COUNT_STREAMS, RECORDING
from test_sessions import start_session


def open_pronunciation(page, servers, **consents):
    call_api(servers, "PUT", "/users/consents", consents, token=browser_token(page))
    page.add_init_script(COUNT_STREAMS)
    page.add_init_script(FAKE_RECOGNITION)
    page.reload()
    expect(page.locator("#dashboard-page")).to_be_visible()
    page.click("#lang-toggle")
    start_session(page, "pronunciation")


def record(page):
    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    page.click("#record-btn")
    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)


def test_record_play_back_and_rate_yourself(page, servers, account):
    open_pronunciation(page, servers, recordings=True, speech_recognition=False)
    record(page)
    expect(page.locator("#play-recording")).to_have_text("▶ Odsłuchaj nagranie")

    page.click("#submit-answer")  # not rated yet
    expect(page.locator("#feedback")).to_have_text("Najpierw wybierz, jak poszło.")

    page.click("#rate-said")
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_contain_text("Poprawnie!")
    assert page.evaluate("window.__recognitionStarts") == 0  # no consent, no recognition


def test_without_recording_the_person_can_still_rate_and_go_on(page, servers, account):
    open_pronunciation(page, servers, recordings=False, speech_recognition=False)

    page.click("#rate-not-yet")
    page.click("#submit-answer")

    expect(page.locator("#feedback")).to_contain_text("Nic nie szkodzi")
    expect(page.locator("#next-exercise")).to_be_visible()


def test_recognition_runs_during_the_recording_and_only_suggests(page, servers, account):
    open_pronunciation(page, servers, recordings=True, speech_recognition=True)

    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    assert page.evaluate("window.__recognitionStarts") == 1  # while recording, not after
    page.click("#record-btn")
    expect(page.locator("#heard")).to_contain_text("hello")

    page.click("#rate-not-yet")  # the person's own rating decides
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_contain_text("Nic nie szkodzi")
