"""Messages in the app, in plain words, never browser pop-ups (U12, P2-4b).

The shared page fixture fails any test in which a browser dialog
(alert, confirm) appears, so every e2e test checks this too.
"""
import pytest
from playwright.sync_api import expect
from test_sessions import choose, start_session

TEXT = {
    "en": {
        "login": "The username or password is not right.",
        "leave": "Leave this session?", "stay": "Stay", "go": "Leave",
        "done": "Session finished. Your score: 100%.",
        "empty": "Choose or type an answer first.",
    },
    "pl": {
        "login": "Nazwa użytkownika lub hasło są nieprawidłowe.",
        "leave": "Wyjść z tej sesji?", "stay": "Zostań", "go": "Wyjdź",
        "done": "Sesja zakończona. Twój wynik: 100%.",
        "empty": "Najpierw wybierz lub wpisz odpowiedź.",
    },
}


def in_polish_if(page, language):
    if language == "pl":
        page.click("#lang-toggle")


@pytest.mark.parametrize("language", ["en", "pl"])
def test_a_wrong_login_is_explained_under_the_form(page, language):
    in_polish_if(page, language)
    page.fill("#login-username", "nobody")
    page.fill("#login-password", "not a password")
    page.click("#login-form-submit button[type=submit]")

    message = page.locator("#login-message")
    expect(message).to_have_text(TEXT[language]["login"])
    expect(message).to_have_attribute("role", "alert")


@pytest.mark.parametrize("language", ["en", "pl"])
def test_leaving_a_session_asks_in_the_app(page, account, language):
    in_polish_if(page, language)
    start_session(page)
    text = TEXT[language]

    page.click("#exit-exercise")
    dialog = page.locator("#leave-dialog")
    expect(dialog).to_contain_text(text["leave"])
    dialog.get_by_role("button", name=text["stay"], exact=True).click()
    expect(dialog).to_be_hidden()
    expect(page.locator("#exercise-counter")).to_have_text("1/5")

    page.click("#exit-exercise")
    dialog.get_by_role("button", name=text["go"], exact=True).click()
    expect(page.locator("#dashboard-page")).to_be_visible()


@pytest.mark.parametrize("language", ["en", "pl"])
def test_the_result_is_shown_in_the_app(page, account, language):
    in_polish_if(page, language)
    start_session(page)
    for number in range(1, 6):
        expect(page.locator("#exercise-counter")).to_have_text(f"{number}/5")
        choose(page)
        page.click("#submit-answer")
        page.click("#next-exercise")

    expect(page.locator("#dashboard-page")).to_be_visible()
    expect(page.locator("#app-message")).to_have_text(TEXT[language]["done"])


def test_submitting_nothing_says_what_to_do(page, account):
    start_session(page)

    page.click("#submit-answer")

    expect(page.locator("#feedback")).to_have_text(TEXT["en"]["empty"])
    expect(page.locator("#exercise-counter")).to_have_text("1/5")
