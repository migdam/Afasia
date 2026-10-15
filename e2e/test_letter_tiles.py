"""Letter tiles in the browser (P2-6b)."""
from playwright.sync_api import expect
from test_full_flow import NAMING_ANSWERS
from test_sessions import start_session


def tap(page, letter):
    page.locator(f"#letter-tiles .tile:not([disabled])[data-letter='{letter}']").first.click()


def test_a_word_can_be_built_from_tiles_with_an_undo(page, account):
    page.click("#lang-toggle")
    start_session(page, "word_naming")
    word = NAMING_ANSWERS[page.inner_text("#exercise-question-text")]
    button = page.locator("#use-tiles")
    expect(button).to_have_text("Ułóż z liter")

    button.click()
    expect(page.locator("#letter-tiles .tile")).to_have_count(len(word))
    tap(page, word[0])
    tap(page, word[1])
    page.click("#tiles-undo")  # take the last letter back
    expect(page.locator("#answer-input")).to_have_value(word[0])
    for letter in word[1:]:
        tap(page, letter)
    expect(page.locator("#answer-input")).to_have_value(word)
    expect(page.locator("#letter-tiles .tile:not([disabled])")).to_have_count(0)
    page.click("#submit-answer")

    expect(page.locator("#feedback")).to_contain_text("Poprawnie!")
