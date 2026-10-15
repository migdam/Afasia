"""Therapy sessions in the browser: answering, feedback, and the server's score."""
import json
from pathlib import Path

from playwright.sync_api import expect

# Sentence completion, both languages: sentence → answer (backend/content/).
SENTENCES = json.loads((Path(__file__).resolve().parents[1] / "backend/content/sentences.json").read_text())["items"]
ANSWERS = {item[language]["sentence"]: item[language]["answer"] for item in SENTENCES for language in ("en", "pl")}


def leave_session(page):
    """Leave the session through the in-app dialog (P2-4b)."""
    page.click("#exit-exercise")
    page.click("#leave-go")


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
        page.click("#next-exercise")

    expect(page.locator("#dashboard-page")).to_be_visible()
    expect(page.locator("#app-message")).to_have_text("Session finished. Your score: 80%.")
    expect(page.locator("#recent-sessions")).to_contain_text("80%")
    expect(page.locator("#badge-count")).to_have_text("1")  # the first-session badge


def test_double_clicking_submit_sends_the_answer_once(page, account):
    start_session(page)
    choose(page)

    page.dblclick("#submit-answer")

    expect(page.locator("#feedback")).to_have_text("Correct! Well done!")
    page.click("#next-exercise")
    expect(page.locator("#exercise-counter")).to_have_text("2/5")
    # A second submission would get "already answered"; the fixture fails on any pop-up.


def test_a_typed_answer_is_not_carried_into_the_next_session(page, account):
    start_session(page, "word_naming")
    page.fill("#answer-input", "cat")
    leave_session(page)
    start_session(page)

    page.click("#submit-answer")  # no option chosen

    # Nothing was carried over, so the app asks for an answer, in words.
    expect(page.locator("#feedback")).to_have_text("Choose or type an answer first.")
    expect(page.locator("#exercise-counter")).to_have_text("1/5")


def test_leaving_during_feedback_does_not_move_the_next_session_on(page, account):
    start_session(page)
    choose(page)
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_be_visible()
    leave_session(page)  # while the feedback is still showing
    start_session(page)

    page.wait_for_timeout(2500)  # nothing moves it on by itself (U4)

    expect(page.locator("#exercise-counter")).to_have_text("1/5")


def test_only_exercise_types_with_content_are_offered(page, account):
    for menu in ("#exercise-type", "#schedule-type"):
        values = page.locator(f"{menu} option").evaluate_all("options => options.map(o => o.value)")
        assert "image_recognition" not in values, menu


def test_starting_exercises_loads_no_missing_files(page, account):
    failed = []
    page.on("response", lambda response: failed.append(response.url) if response.status >= 400 else None)

    for exercise_type in ("word_naming", "pronunciation"):
        start_session(page, exercise_type)
        expect(page.locator("#exercise-image")).to_be_hidden()
        leave_session(page)

    assert failed == []
