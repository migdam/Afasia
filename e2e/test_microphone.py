"""The microphone is on only while recording (P1-6a).

Chromium runs with a fake microphone (see conftest), and the page counts
the streams it opens, so the tests can see whether any is still live.
"""
import re

from playwright.sync_api import expect
from conftest import browser_token, call_api
from test_sessions import leave_session, start_session

RECORDING = re.compile(r"\brecording\b")
COUNT_STREAMS = """
window.__micStreams = [];
const getUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
navigator.mediaDevices.getUserMedia = async (constraints) => {
    const stream = await getUserMedia(constraints);
    window.__micStreams.push(stream);
    return stream;
};
"""


def live_microphones(page):
    return page.evaluate(
        "window.__micStreams.flatMap(s => s.getTracks()).filter(t => t.readyState === 'live').length"
    )


def start_recording(page, servers):
    # Consent is asked for in the app (test_consent_questions.py); here it is given up front.
    call_api(servers, "PUT", "/users/consents", {"recordings": True}, token=browser_token(page))
    page.add_init_script(COUNT_STREAMS)
    page.reload()
    expect(page.locator("#dashboard-page")).to_be_visible()
    start_session(page, "pronunciation")
    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    assert live_microphones(page) == 1


def test_the_microphone_turns_off_when_a_recording_stops(page, servers, account):
    start_recording(page, servers)

    page.click("#record-btn")

    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)
    assert live_microphones(page) == 0


def test_a_second_recording_turns_it_on_and_off_again(page, servers, account):
    start_recording(page, servers)
    page.click("#record-btn")
    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)

    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    assert live_microphones(page) == 1
    page.click("#record-btn")
    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)
    assert live_microphones(page) == 0


def test_leaving_the_session_mid_recording_turns_it_off(page, servers, account):
    start_recording(page, servers)

    leave_session(page)

    expect(page.locator("#dashboard-page")).to_be_visible()
    page.wait_for_function("() => window.__micStreams.every(s => s.getTracks().every(t => t.readyState === 'ended'))")


def test_logging_out_mid_recording_turns_it_off(page, servers, account):
    start_recording(page, servers)

    page.click("#logout-btn")

    expect(page.locator("#auth-page")).to_be_visible()
    page.wait_for_function("() => window.__micStreams.every(s => s.getTracks().every(t => t.readyState === 'ended'))")
