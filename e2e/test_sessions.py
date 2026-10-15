"""Therapy sessions in the browser: answering, feedback, and the server's score."""
import json
from pathlib import Path

from playwright.sync_api import expect

# Sentence completion, both languages: sentence → answer (backend/content/).
SENTENCES = json.loads((Path(__file__).resolve().parents[1] / "backend/content/sentences.json").read_text())["items"]
ANSWERS = {item[language]["sentence"]: item[language]["answer"] for item in SENTENCES for language in ("en", "pl")}


def record_dialogs(page):
    """Accept every alert and confirm, and return the list of their messages."""
    messages = []

    def on_dialog(dialog):
        messages.append(dialog.message)
        dialog.accept()

    page.on("dialog", on_dialog)
    return messages


def start_session(page, exercise_type="sentence_completion"):
    page.select_option("#exercise-type", exercise_type)
    page.select_option("#difficulty", "easy")
    page.fill("#num-exercises", "5")
    page.click("#new-session-form button[type=submit]")
    expect(page.locator("#exercise-counter")).to_have_text("1/5")


def choose(page, correct=True):
    """Pick the right option, or a wrong one; returns the right answer."""
    right = ANSWERS[page.inner_text("#exercise-question-text")]
    options = page.locator(".option-btn").all_inner_texts()
    choice = right if correct else next(o for o in options if o != right)
    page.click(f".option-btn[data-answer='{choice}']")
    return right


def test_a_session_gives_feedback_and_ends_with_the_server_score(page, account):
    dialogs = record_dialogs(page)
    start_session(page)

    for number in range(1, 6):
        expect(page.locator("#exercise-counter")).to_have_text(f"{number}/5")
        # Answer the first exercise wrongly and the rest correctly: 4 of 5.
        right = choose(page, correct=number > 1)
        page.click("#submit-answer")

        feedback = page.locator("#feedback")
        expect(feedback).to_be_visible()
        if number == 1:
            expect(feedback).to_have_text(f"Not quite. Correct answer: {right}")
        else:
            expect(feedback).to_have_text("Correct! Well done!")

    expect(page.locator("#dashboard-page")).to_be_visible(timeout=10_000)
    assert dialogs == ["Session complete! Score: 80%"]
    expect(page.locator("#recent-sessions")).to_contain_text("80%")
    expect(page.locator("#badge-count")).to_have_text("1")  # the first-session badge


def test_double_clicking_submit_sends_the_answer_once(page, account):
    dialogs = record_dialogs(page)
    start_session(page)
    choose(page)

    page.dblclick("#submit-answer")

    expect(page.locator("#feedback")).to_have_text("Correct! Well done!")
    expect(page.locator("#exercise-counter")).to_have_text("2/5")
    assert dialogs == []  # a second submission would get "already answered"


def test_a_typed_answer_is_not_carried_into_the_next_session(page, account):
    record_dialogs(page)
    start_session(page, "word_naming")
    page.fill("#answer-input", "cat")
    page.click("#exit-exercise")
    start_session(page)

    with page.expect_event("dialog") as dialog:
        page.click("#submit-answer")  # no option chosen

    assert dialog.value.message == "Please provide an answer"
    expect(page.locator("#feedback")).to_be_hidden()


def test_leaving_during_feedback_does_not_move_the_next_session_on(page, account):
    record_dialogs(page)
    start_session(page)
    choose(page)
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_be_visible()
    page.click("#exit-exercise")  # while the feedback is still showing
    start_session(page)

    page.wait_for_timeout(2500)  # longer than the feedback pause

    expect(page.locator("#exercise-counter")).to_have_text("1/5")


def test_only_exercise_types_with_content_are_offered(page, account):
    for menu in ("#exercise-type", "#schedule-type"):
        values = page.locator(f"{menu} option").evaluate_all("options => options.map(o => o.value)")
        assert "image_recognition" not in values, menu


def test_starting_exercises_loads_no_missing_files(page, account):
    record_dialogs(page)  # accepts the confirmation when leaving
    failed = []
    page.on("response", lambda response: failed.append(response.url) if response.status >= 400 else None)

    for exercise_type in ("word_naming", "pronunciation"):
        start_session(page, exercise_type)
        expect(page.locator("#exercise-image")).to_be_hidden()
        page.click("#exit-exercise")

    assert failed == []
