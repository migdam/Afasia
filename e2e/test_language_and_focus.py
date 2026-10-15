"""The page says which language it is in, and the focus goes where the
person needs it (P2-4e). Screen readers use both."""
from playwright.sync_api import expect
from test_sessions import choose, start_session

def test_the_page_language_follows_the_chosen_language(page):
    assert page.evaluate("document.documentElement.lang") == "en"

    page.click("#lang-toggle")
    assert page.evaluate("document.documentElement.lang") == "pl"

    page.reload()
    assert page.evaluate("document.documentElement.lang") == "pl"

def test_changing_page_moves_the_focus_to_its_heading(page, account):
    page.click(".nav-item[data-page='progress']")
    expect(page.locator("#progress-page h2")).to_be_focused()

    page.click(".nav-item[data-page='account']")
    expect(page.locator("#account-page h2")).to_be_focused()

def test_each_exercise_puts_the_focus_on_its_question(page, account):
    start_session(page)
    expect(page.locator("#exercise-question-text")).to_be_focused()

    choose(page)
    page.click("#submit-answer")
    page.click("#next-exercise")

    expect(page.locator("#exercise-counter")).to_have_text("2/5")
    expect(page.locator("#exercise-question-text")).to_be_focused()

def test_after_logging_out_the_focus_is_on_the_login_page(page, account):
    page.click("#logout-btn")

    expect(page.locator("#auth-page h2")).to_be_focused()
