"""The microphone is on only while recording (P1-6a).

Chromium runs with a fake microphone (see conftest), and the page counts
the streams it opens, so the tests can see whether any is still live.
"""
import re

from playwright.sync_api import expect
from test_sessions import record_dialogs, start_session

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


def start_recording(page):
    page.add_init_script(COUNT_STREAMS)
    page.reload()
    expect(page.locator("#dashboard-page")).to_be_visible()
    start_session(page, "pronunciation")
    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    assert live_microphones(page) == 1


def test_the_microphone_turns_off_when_a_recording_stops(page, account):
    start_recording(page)

    page.click("#record-btn")

    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)
    assert live_microphones(page) == 0


def test_a_second_recording_turns_it_on_and_off_again(page, account):
    start_recording(page)
    page.click("#record-btn")
    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)

    page.click("#record-btn")
    expect(page.locator("#record-btn")).to_have_class(RECORDING)
    assert live_microphones(page) == 1
    page.click("#record-btn")
    expect(page.locator("#record-btn")).not_to_have_class(RECORDING)
    assert live_microphones(page) == 0


def test_leaving_the_session_mid_recording_turns_it_off(page, account):
    record_dialogs(page)  # accepts "Are you sure you want to exit?"
    start_recording(page)

    page.click("#exit-exercise")

    expect(page.locator("#dashboard-page")).to_be_visible()
    page.wait_for_function("() => window.__micStreams.every(s => s.getTracks().every(t => t.readyState === 'ended'))")


def test_logging_out_mid_recording_turns_it_off(page, account):
    start_recording(page)

    page.click("#logout-btn")

    expect(page.locator("#auth-page")).to_be_visible()
    page.wait_for_function("() => window.__micStreams.every(s => s.getTracks().every(t => t.readyState === 'ended'))")
