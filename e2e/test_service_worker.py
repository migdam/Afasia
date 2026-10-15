"""No service worker any more, and the old one cleans up after itself (P1-7).

The old worker served the app's files from its cache forever, and cached
API responses too, personal data included. These tests use their own
browser context, because the shared fixture blocks service workers.
"""
import json
import time

import pytest

REGISTRATIONS = "navigator.serviceWorker.getRegistrations().then(r => r.length)"
CACHES = "caches.keys()"


@pytest.fixture
def sw_page(browser, servers):
    context = browser.new_context()  # service workers allowed
    context.add_init_script(f"window.API_BASE_URL = {json.dumps(servers['api'])};")
    page = context.new_page()
    yield page
    context.close()


def test_the_app_no_longer_installs_a_service_worker(sw_page, servers):
    sw_page.goto(servers["web"])
    sw_page.wait_for_load_state("networkidle")
    sw_page.wait_for_timeout(500)

    assert sw_page.evaluate(REGISTRATIONS) == 0


def test_a_device_with_the_old_worker_drops_it_and_its_caches(sw_page, servers):
    sw_page.goto(servers["web"])
    # What the old worker left behind: a cache with app files and API data.
    sw_page.evaluate("""async () => {
        const cache = await caches.open('aphasia-therapy-v1');
        await cache.put('/js/app.js', new Response('old code'));
        await cache.put('/api/v1/users/profile', new Response('{"username": "someone"}'));
    }""")
    # The browser fetching /sw.js again is how an installed worker updates.
    sw_page.evaluate("navigator.serviceWorker.register('/sw.js')")

    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        state = (sw_page.evaluate(REGISTRATIONS), sw_page.evaluate(CACHES))
        if state == (0, []):
            break
        sw_page.wait_for_timeout(200)
    assert state == (0, []), f"registrations, caches: {state}"
