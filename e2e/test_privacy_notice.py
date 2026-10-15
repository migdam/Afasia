"""The privacy notice: reachable before and after logging in, in EN and PL (P1-6d)."""
from urllib.parse import urlparse

import pytest
from playwright.sync_api import expect

HEADING = {"en": "Privacy notice", "pl": "Informacja o prywatności"}


@pytest.mark.parametrize("language", ["en", "pl"])
def test_the_login_page_links_to_the_notice_in_your_language(page, servers, language):
    if language == "pl":
        page.click("#lang-toggle")
    requests = []
    page.on("request", lambda request: requests.append(request.url))

    page.click("#auth-page .privacy-link")

    expect(page).to_have_url(f"{servers['web']}/privacy.html#{language}")
    heading = page.locator(f"section#{language} h1")
    expect(heading).to_have_text(HEADING[language])
    expect(heading).to_be_in_viewport()
    web = urlparse(servers["web"]).netloc
    assert all(urlparse(url).netloc == web for url in requests), requests  # nothing from elsewhere


def test_the_account_page_links_to_it_too(page, account):
    page.click(".nav-item[data-page='account']")

    page.click("#account-page .privacy-link")

    expect(page.locator("section#en h1")).to_have_text(HEADING["en"])
    page.click("section#en .back-to-app")
    expect(page.locator("#dashboard-page")).to_be_visible()  # still logged in


def test_the_notice_marks_what_only_the_operator_can_fill_in(page, servers):
    page.goto(f"{servers['web']}/privacy.html")

    for language in ("en", "pl"):
        section = page.locator(f"section#{language}")
        expect(section).to_have_attribute("lang", language)
        assert section.locator(".to-complete").count() >= 3
