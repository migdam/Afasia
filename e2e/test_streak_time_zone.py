"""The browser tells the app its time zone, for streak days (P2-9b)."""
import json
import uuid

from playwright.sync_api import expect

from conftest import PASSWORD, browser_token, call_api


def test_the_browser_sends_its_time_zone(browser, servers):
    context = browser.new_context(timezone_id="Europe/Warsaw")
    context.add_init_script(f"window.API_BASE_URL = {json.dumps(servers['api'])};")
    page = context.new_page()
    try:
        page.goto(servers["web"])
        username = f"pat{uuid.uuid4().hex[:8]}"
        page.click("#show-register")
        page.fill("#register-email", f"{username}@example.com")
        page.fill("#register-username", username)
        page.fill("#register-password", PASSWORD)
        page.click("#register-form-submit button[type=submit]")
        expect(page.locator("#dashboard-page")).to_be_visible()

        token = browser_token(page)
        for _ in range(50):  # sent in the background, after the dashboard shows
            if call_api(servers, "GET", "/users/time-zone", token=token)[1]["time_zone"]:
                break
            page.wait_for_timeout(100)
        assert call_api(servers, "GET", "/users/time-zone", token=token)[1] == {"time_zone": "Europe/Warsaw"}
    finally:
        context.close()
