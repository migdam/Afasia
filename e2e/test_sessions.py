"""A therapy session in the browser: feedback on each answer, then the server's score."""
from playwright.sync_api import expect

# The easy sentence-completion items in backend/app/api/v1/endpoints/therapy.py.
ANSWERS = {"The sky is ___": "blue", "I am ___": "happy", "The sun is ___": "bright"}


def test_a_session_gives_feedback_and_ends_with_the_server_score(page, account):
    alerts = []

    def on_dialog(dialog):
        alerts.append(dialog.message)
        dialog.accept()

    page.on("dialog", on_dialog)
    page.select_option("#exercise-type", "sentence_completion")
    page.select_option("#difficulty", "easy")
    page.fill("#num-exercises", "5")
    page.click("#new-session-form button[type=submit]")

    for number in range(1, 6):
        expect(page.locator("#exercise-counter")).to_have_text(f"{number}/5")
        right = ANSWERS[page.inner_text("#exercise-question-text")]
        options = page.locator(".option-btn").all_inner_texts()
        # Answer the first exercise wrongly and the rest correctly: 4 of 5.
        choice = right if number > 1 else next(o for o in options if o != right)

        page.click(f".option-btn[data-answer='{choice}']")
        page.click("#submit-answer")

        feedback = page.locator("#feedback")
        expect(feedback).to_be_visible()
        if number == 1:
            expect(feedback).to_have_text(f"Not quite. Correct answer: {right}")
        else:
            expect(feedback).to_have_text("Correct! Well done!")

    expect(page.locator("#dashboard-page")).to_be_visible(timeout=10_000)
    assert alerts == ["Session complete! Score: 80%"]
    expect(page.locator("#recent-sessions")).to_contain_text("80%")
