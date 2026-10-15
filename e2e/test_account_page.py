"""Changing your password on the Account page (P1-5e2)."""
import pytest
from conftest import PASSWORD, call_api
from playwright.sync_api import expect

NEW = "a brand new passphrase"
TEXT = {
    "en": {"changed": "Your password has been changed.", "wrong": "The current password is not right."},
    "pl": {"changed": "Hasło zostało zmienione.", "wrong": "Obecne hasło jest nieprawidłowe."},
}


def change_password(page, current, new):
    page.click(".nav-item[data-page='account']")
    page.fill("#current-password", current)
    page.fill("#new-password", new)
    page.click("#password-form button[type=submit]")


def log_in(page, username, password):
    page.fill("#login-username", username)
    page.fill("#login-password", password)
    page.click("#login-form-submit button[type=submit]")


@pytest.mark.parametrize("language", ["en", "pl"])
def test_a_new_password_replaces_the_old_one(page, servers, account, language):
    if language == "pl":
        page.click("#lang-toggle")

    change_password(page, PASSWORD, NEW)

    expect(page.locator("#password-message")).to_contain_text(TEXT[language]["changed"])
    expect(page.locator("#current-password")).to_have_value("")  # nothing left on screen
    page.reload()  # still logged in, with the new login
    expect(page.locator("#dashboard-page")).to_be_visible()

    page.click("#logout-btn")
    log_in(page, account, NEW)
    expect(page.locator("#dashboard-page")).to_be_visible()
    status, _ = call_api(servers, "POST", "/auth/login", {"username": account, "password": PASSWORD})
    assert status == 401


@pytest.mark.parametrize("language", ["en", "pl"])
def test_a_wrong_current_password_is_explained_in_words(page, account, language):
    if language == "pl":
        page.click("#lang-toggle")

    change_password(page, "not my password", NEW)

    message = page.locator("#password-message")
    expect(message).to_have_text(TEXT[language]["wrong"])
    expect(message).to_have_attribute("role", "alert")


def test_the_form_is_labelled(page, account):
    page.click(".nav-item[data-page='account']")

    for field in ("#current-password", "#new-password"):
        expect(page.locator(field)).to_have_attribute("autocomplete", "current-password" if "current" in field else "new-password")
        assert page.locator(f"label[for='{field[1:]}']").is_visible()
    expect(page.locator("#new-password")).to_have_attribute("minlength", "8")
