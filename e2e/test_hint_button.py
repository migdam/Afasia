"""The hint button in naming exercises (P2-3b)."""
import pytest
from playwright.sync_api import expect

TEXT = {
    "en": {"button": "Hint", "first": "Group:", "second": "It starts with:", "third": "The word is:",
           "used": "Hints used: 3"},
    "pl": {"button": "Podpowiedź", "first": "Grupa:", "second": "Zaczyna się na:", "third": "To słowo to:",
           "used": "Użyte podpowiedzi: 3"},
}


def start(page, exercise_type):
    page.select_option("#exercise-type", exercise_type)
    page.select_option("#difficulty", "easy")
    page.fill("#num-exercises", "5")
    page.click("#new-session-form button[type=submit]")
    expect(page.locator("#exercise-counter")).to_have_text("1/5")


@pytest.mark.parametrize("language", ["en", "pl"])
def test_three_hints_then_the_word_and_the_feedback_counts_them(page, account, language):
    text = TEXT[language]
    if language == "pl":
        page.click("#lang-toggle")
    start(page, "word_naming")
    button, hints = page.locator("#hint-btn"), page.locator("#hint-list li")
    expect(button).to_have_text(text["button"])

    for _ in range(3):
        button.click()
    expect(hints).to_have_count(3)
    expect(hints.nth(0)).to_contain_text(text["first"])
    expect(hints.nth(1)).to_contain_text(text["second"])
    expect(hints.nth(2)).to_contain_text(text["third"])
    expect(button).to_be_disabled()
    expect(page.locator("#hint-list")).to_have_attribute("aria-live", "polite")

    word = hints.nth(2).locator("span").first.inner_text().split(":", 1)[1].strip()
    page.fill("#answer-input", word)
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_contain_text(text["used"])

    page.click("#next-exercise")
    expect(page.locator("#exercise-counter")).to_have_text("2/5")
    expect(hints).to_have_count(0)  # a fresh start for the next word
    expect(button).to_be_enabled()


def test_only_naming_offers_hints(page, account):
    start(page, "sentence_completion")

    expect(page.locator("#hint-btn")).to_be_hidden()
