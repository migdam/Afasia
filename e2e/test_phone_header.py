"""On a phone the header doesn't cover the exercise (P2-4g)."""
import pytest
from playwright.sync_api import expect
from test_sessions import start_session

# Whether the element is what the person sees at its own centre, i.e. not
# covered by anything else (the header, say).
UNCOVERED = """(selector) => {
    const target = document.querySelector(selector);
    target.scrollIntoView({ block: 'start' });  // as when reading down the page
    const box = target.getBoundingClientRect();
    const seen = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
    return seen === target || target.contains(seen);
}"""


@pytest.mark.parametrize("large_text", [False, True], ids=["normal-text", "large-text"])
def test_on_a_phone_the_question_is_not_covered(page, account, large_text):
    page.set_viewport_size({"width": 375, "height": 740})
    if large_text:
        page.click("#text-size")
    start_session(page, "word_naming")

    for selector in ("#exercise-question-text", "#answer-input", "#submit-answer"):
        assert page.evaluate(UNCOVERED, selector), selector


def test_on_a_phone_the_header_is_one_short_row(page, account):
    page.set_viewport_size({"width": 375, "height": 740})

    height = page.evaluate("document.querySelector('.navbar').getBoundingClientRect().height")

    assert height <= 100, height
    expect(page.locator("#logout-btn")).to_be_hidden()  # it lives on the Account page there


def test_the_account_page_has_a_log_out_button(page, account):
    page.set_viewport_size({"width": 375, "height": 740})
    page.click(".nav-item[data-page='account']")

    page.click("#account-logout")

    expect(page.locator("#auth-page")).to_be_visible()
