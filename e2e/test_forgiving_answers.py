"""Forgiving answers in the browser (P2-5): no Polish letters needed, and a
near miss is called "almost"."""
from playwright.sync_api import expect
from test_full_flow import NAMING_ANSWERS
from test_sessions import start_session

PLAIN = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")


def polish_naming(page):
    page.click("#lang-toggle")
    start_session(page, "word_naming")
    return NAMING_ANSWERS[page.inner_text("#exercise-question-text")]


def test_polish_typed_without_its_special_letters_is_right(page, account):
    word = polish_naming(page)

    page.fill("#answer-input", word.translate(PLAIN).upper())
    page.click("#submit-answer")

    expect(page.locator("#feedback")).to_contain_text("Poprawnie!")


def test_a_near_miss_is_called_almost_and_the_practice_try_is_forgiving_too(page, account):
    word = polish_naming(page)

    page.fill("#answer-input", word[1] + word[0] + word[2:])  # two letters swapped
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_contain_text("Prawie.")
    expect(page.locator("#feedback strong")).to_have_text(word)

    page.click("#try-again")
    page.fill("#answer-input", f"  {word.translate(PLAIN)} ")
    page.click("#submit-answer")
    expect(page.locator("#feedback")).to_contain_text("Tak jest.")
