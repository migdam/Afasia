"""Read aloud (U3, P2-4d), only with voices on the person's own device.

The browser's speech engine is replaced by a fake that records what it is
asked to say, with which voice; the voices on offer are set per test.
"""
import json

import pytest
from playwright.sync_api import expect
from test_sessions import start_session

FAKE_SPEECH = """
window.__spoken = [];
window.__voices = %s;
class FakeUtterance { constructor(text) { this.text = text; } }
window.SpeechSynthesisUtterance = FakeUtterance;
Object.defineProperty(window, 'speechSynthesis', { value: {
    getVoices: () => window.__voices,
    speak: (u) => window.__spoken.push({ text: u.text, lang: u.lang, voice: u.voice && u.voice.name }),
    cancel: () => {},
    addEventListener: () => {},
}});
"""
LOCAL = [{"name": "Local EN", "lang": "en-GB", "localService": True},
         {"name": "Local PL", "lang": "pl-PL", "localService": True},
         {"name": "Cloud PL", "lang": "pl-PL", "localService": False}]
REMOTE_ONLY = [{"name": "Cloud EN", "lang": "en-US", "localService": False}]
LABEL = {"en": "Read aloud", "pl": "Przeczytaj"}


def with_voices(page, voices):
    page.add_init_script(FAKE_SPEECH % json.dumps(voices))
    page.reload()
    expect(page.locator("#dashboard-page")).to_be_visible()


def spoken(page):
    return page.evaluate("window.__spoken")


@pytest.mark.parametrize("language", ["en", "pl"])
def test_the_question_is_read_in_the_chosen_language_with_a_local_voice(page, account, language):
    with_voices(page, LOCAL)
    if language == "pl":
        page.click("#lang-toggle")
    start_session(page, "word_naming")
    button = page.locator("#read-question")
    expect(button).to_contain_text(LABEL[language])

    button.click()

    question = page.inner_text("#exercise-question-text")
    [said] = spoken(page)
    assert said["text"] == question
    assert said["lang"].startswith(language)
    assert said["voice"] == ("Local PL" if language == "pl" else "Local EN")  # never "Cloud PL"


def test_hints_and_feedback_can_be_read_too(page, account):
    with_voices(page, LOCAL)
    start_session(page, "word_naming")
    page.click("#hint-btn")
    page.locator("#hint-list li .read-aloud").click()
    page.fill("#answer-input", "not it")
    page.click("#submit-answer")
    page.click("#read-feedback")

    texts = [s["text"] for s in spoken(page)]
    assert texts[0] == page.locator("#hint-list li span").first.inner_text()
    assert texts[1].startswith("Not quite.")


def test_the_gap_in_a_sentence_is_read_as_a_pause(page, account):
    with_voices(page, LOCAL)
    start_session(page, "sentence_completion")

    page.click("#read-question")

    assert "___" not in spoken(page)[0]["text"]


def test_without_a_voice_on_the_device_there_is_no_read_aloud(page, account):
    with_voices(page, REMOTE_ONLY)
    start_session(page, "word_naming")

    expect(page.locator("#read-question")).to_be_hidden()
    assert spoken(page) == []
