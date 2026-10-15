"""The whole flow, in English and in Polish (backlog P0-7's acceptance test).

Sign up, do one session of each exercise type that works, get feedback in
the chosen language, and find the right scores on the dashboard and the
progress page. Pronunciation is left out: it needs a microphone and speech
recognition, and is redesigned in backlog P2-7. The exercise content itself
is still English-only (P2-2).
"""
import pytest
from playwright.sync_api import expect
from test_sessions import ANSWERS as SENTENCE_ANSWERS
from test_sessions import record_dialogs

# The easy word-naming items in backend/app/api/v1/endpoints/therapy.py.
NAMING_ANSWERS = {
    "What is it? A small pet that purrs and says meow.": "cat",
    "What is it? A pet that barks and wags its tail.": "dog",
    "What is it? A building where a family lives.": "house",
    "What is it? You drive it on the road. It has four wheels.": "car",
    "What is it? A tall plant with a trunk, branches and leaves.": "tree",
}
TEXT = {
    "en": {"label": "EN", "right": "Correct! Well done!", "wrong": "Not quite. Correct answer: {}"},
    "pl": {"label": "PL", "right": "Poprawnie! Świetna robota!", "wrong": "Nie tym razem. Prawidłowa odpowiedź: {}"},
}


def play_session(page, exercise_type, text, wrong_first):
    page.select_option("#exercise-type", exercise_type)
    page.select_option("#difficulty", "easy")
    page.fill("#num-exercises", "5")
    page.click("#new-session-form button[type=submit]")

    for number in range(1, 6):
        expect(page.locator("#exercise-counter")).to_have_text(f"{number}/5")
        question = page.inner_text("#exercise-question-text")
        wrong = wrong_first and number == 1
        if exercise_type == "word_naming":
            right = NAMING_ANSWERS[question]
            page.fill("#answer-input", "not it" if wrong else right)
        else:
            right = SENTENCE_ANSWERS[question]
            options = page.locator(".option-btn").all_inner_texts()
            choice = next(o for o in options if o != right) if wrong else right
            page.click(f".option-btn[data-answer='{choice}']")
        page.click("#submit-answer")

        feedback = page.locator("#feedback")
        expect(feedback).to_be_visible()
        expect(feedback).to_have_text(text["wrong"].format(right) if wrong else text["right"])

    expect(page.locator("#dashboard-page")).to_be_visible(timeout=10_000)


@pytest.mark.parametrize("language", ["en", "pl"])
def test_the_whole_flow(page, account, language):
    text = TEXT[language]
    record_dialogs(page)
    if language == "pl":
        page.click("#lang-toggle")
    expect(page.locator("#lang-text")).to_have_text(text["label"])

    play_session(page, "word_naming", text, wrong_first=True)  # 4 of 5
    play_session(page, "sentence_completion", text, wrong_first=False)  # 5 of 5

    recent = page.locator("#recent-sessions")
    expect(recent).to_contain_text("80%")
    expect(recent).to_contain_text("100%")
    page.click(".nav-item[data-page='progress']")
    expect(page.locator("#progress-total-sessions")).to_have_text("2")
    expect(page.locator("#progress-avg-accuracy")).to_have_text("90%")  # 9 of 10
