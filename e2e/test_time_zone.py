"""Planned sessions show at the time they were planned for, in the person's
own time zone (P1-8d)."""
import json
import uuid

from conftest import PASSWORD
from playwright.sync_api import expect


def test_a_session_planned_for_10_am_in_warsaw_shows_at_10_am(browser, servers):
    context = browser.new_context(timezone_id="Europe/Warsaw", locale="en-GB")
    context.add_init_script(f"window.API_BASE_URL = {json.dumps(servers['api'])};")
    page = context.new_page()
    page.goto(servers["web"])
    username = f"pat{uuid.uuid4().hex[:8]}"
    page.click("#show-register")
    page.fill("#register-email", f"{username}@example.com")
    page.fill("#register-username", username)
    page.fill("#register-password", PASSWORD)
    page.click("#register-form-submit button[type=submit]")
    expect(page.locator("#dashboard-page")).to_be_visible()

    page.click("#add-schedule-btn")
    page.fill("#schedule-title", "Morning practice")
    page.fill("#schedule-datetime", "2099-06-01T10:00")
    page.click("#schedule-form button[type=submit]")

    expect(page.locator("#scheduled-list")).to_contain_text("10:00")
    context.close()
