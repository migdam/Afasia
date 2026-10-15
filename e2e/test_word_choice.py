"""Choosing the word instead of typing it, in the browser (P2-6a)."""
import json
from pathlib import Path

from playwright.sync_api import expect
from test_full_flow import NAMING_ANSWERS
from test_sessions import start_session

CONCEPTS = json.loads((Path(__file__).resolve().parents[1] / "backend/content/concepts.json").read_text())["concepts"]
PL_WORDS = {c["pl"]["word"] for c in CONCEPTS}


def test_a_naming_exercise_can_be_answered_by_choosing_a_word(page, account):
    page.click("#lang-toggle")
    start_session(page, "word_naming")
    right = NAMING_ANSWERS[page.inner_text("#exercise-question-text")]
    choose = page.locator("#choose-words")
    expect(choose).to_have_text("Wybierz z listy")

    choose.click()
    options = page.locator("#exercise-options .option-btn")
    expect(options).to_have_count(4)
    assert set(options.all_inner_texts()) <= PL_WORDS
    expect(choose).to_be_hidden()
    page.click(f"#exercise-options .option-btn[data-answer='{right}']")
    page.click("#submit-answer")

    expect(page.locator("#feedback")).to_contain_text("Poprawnie!")
    page.click("#next-exercise")
    expect(page.locator("#exercise-options .option-btn")).to_have_count(0)  # a fresh start
    expect(choose).to_be_visible()


def test_typing_still_works_without_choosing(page, account):
    start_session(page, "word_naming")
    right = NAMING_ANSWERS[page.inner_text("#exercise-question-text")]

    page.fill("#answer-input", right)
    page.click("#submit-answer")

    expect(page.locator("#feedback")).to_contain_text("Correct!")
