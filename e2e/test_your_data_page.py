"""Downloading your data and deleting your account on the Account page (P1-6c2)."""
import json

import pytest
from conftest import PASSWORD, call_api
from playwright.sync_api import expect

TITLE = {"en": "Delete your account?", "pl": "Usunąć Twoje konto?"}


def open_account(page, language="en"):
    if language == "pl":
        page.click("#lang-toggle")
    page.click(".nav-item[data-page='account']")


def test_download_my_data_saves_everything_as_json(page, account):
    open_account(page)

    with page.expect_download() as info:
        page.click("#download-data")

    download = info.value
    assert download.suggested_filename.endswith(".json")
    data = json.loads(open(download.path()).read())
    assert data["account"]["username"] == account


@pytest.mark.parametrize("language", ["en", "pl"])
def test_deleting_asks_for_the_password_and_then_ends_everything(page, servers, account, language):
    open_account(page, language)

    page.click("#delete-account")
    dialog = page.locator("#delete-dialog")
    expect(dialog).to_be_visible()
    expect(dialog).to_contain_text(TITLE[language])
    page.fill("#delete-password", "not my password")
    page.click("#delete-confirm")
    expect(page.locator("#delete-message")).to_have_attribute("role", "alert")
    expect(dialog).to_be_visible()

    page.fill("#delete-password", PASSWORD)
    page.click("#delete-confirm")

    expect(page.locator("#auth-page")).to_be_visible()
    expect(dialog).to_be_hidden()
    status, _ = call_api(servers, "POST", "/auth/login", {"username": account, "password": PASSWORD})
    assert status == 401


def test_cancelling_deletes_nothing(page, servers, account):
    open_account(page)

    page.click("#delete-account")
    page.fill("#delete-password", PASSWORD)
    page.click("#delete-cancel")

    expect(page.locator("#delete-dialog")).to_be_hidden()
    expect(page.locator("#delete-password")).to_have_value("")
    status, _ = call_api(servers, "POST", "/auth/login", {"username": account, "password": PASSWORD})
    assert status == 200


def test_on_a_phone_the_last_button_is_not_hidden_behind_the_menu(page, account):
    page.set_viewport_size({"width": 375, "height": 740})
    open_account(page)

    button = page.locator("#delete-account")
    button.scroll_into_view_if_needed()
    page.mouse.wheel(0, 2000)  # as far down as the page goes

    nav_top = page.locator(".bottom-nav").bounding_box()["y"]
    box = button.bounding_box()
    assert box["y"] + box["height"] <= nav_top
    button.click(timeout=5000)
    expect(page.locator("#delete-dialog")).to_be_visible()
