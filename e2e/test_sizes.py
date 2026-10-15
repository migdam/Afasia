"""Big enough to read and to touch (U1, U5; P2-4c), measured in the browser."""
from playwright.sync_api import expect
from test_sessions import start_session

# Every visible control on the page that is smaller than 48×48 px.
SMALL_TARGETS = """() => [...document.querySelectorAll('button, input, select, .nav-item')]
    .filter((e) => e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden')
    .map((e) => ({ id: e.id || e.className || e.tagName, box: e.getBoundingClientRect() }))
    .filter(({ box }) => box.width < 47.5 || box.height < 47.5)
    .map(({ id, box }) => `${id} ${Math.round(box.width)}x${Math.round(box.height)}`)"""

# Visible text smaller than 18 px.
SMALL_TEXT = """() => [...document.querySelectorAll('body *')]
    .filter((e) => e.offsetParent !== null && [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()))
    .filter((e) => parseFloat(getComputedStyle(e).fontSize) < 17.5)
    .map((e) => `${e.id || e.className || e.tagName}: ${getComputedStyle(e).fontSize} "${e.textContent.trim().slice(0, 20)}"`)"""

CONTRAST = """(selector) => {
    const parse = (c) => c.match(/[\\d.]+/g).slice(0, 3).map(Number);
    const lum = ([r, g, b]) => [r, g, b].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; })
        .reduce((sum, v, i) => sum + v * [0.2126, 0.7152, 0.0722][i], 0);
    const el = document.querySelector(selector);
    let bg = el;
    while (bg && getComputedStyle(bg).backgroundColor.match(/rgba\\(.*, 0\\)|transparent/)) bg = bg.parentElement;
    const [a, b] = [lum(parse(getComputedStyle(el).color)), lum(parse(getComputedStyle(bg).backgroundColor))];
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}"""


def check_page(page, name):
    assert page.evaluate(SMALL_TARGETS) == [], name
    assert page.evaluate(SMALL_TEXT) == [], name


def test_body_text_is_20_px_with_room_between_lines(page):
    size = float(page.evaluate("getComputedStyle(document.body).fontSize").removesuffix("px"))
    line = float(page.evaluate("getComputedStyle(document.body).lineHeight").removesuffix("px"))

    assert size >= 20
    assert line / size >= 1.5


def test_the_login_page_has_big_text_and_targets(page):
    check_page(page, "login")


def test_the_dashboard_account_and_progress_pages_have_big_text_and_targets(page, account):
    check_page(page, "dashboard")
    for name in ("progress", "account"):
        page.click(f".nav-item[data-page='{name}']")
        check_page(page, name)


def test_exercises_have_big_text_and_targets(page, account):
    start_session(page, "word_naming")
    check_page(page, "naming")
    page.click("#exit-exercise")
    page.click("#leave-go")
    start_session(page, "sentence_completion")
    check_page(page, "sentence")


def test_the_language_button_is_readable_in_the_dark_theme(page):
    page.click("#theme-toggle")

    # Colors change with a short transition, so measure once it has ended
    # (polled from here: the page's CSP rightly forbids eval-based waits).
    for _ in range(25):
        ratio = page.evaluate(CONTRAST, "#lang-text")
        if ratio >= 4.5:
            break
        page.wait_for_timeout(200)
    assert ratio >= 4.5


def test_text_can_be_made_larger_and_it_is_remembered(page, account):
    before = float(page.evaluate("getComputedStyle(document.body).fontSize").removesuffix("px"))
    button = page.locator("#text-size")
    expect(button).to_have_attribute("aria-pressed", "false")

    button.click()
    expect(button).to_have_attribute("aria-pressed", "true")
    after = float(page.evaluate("getComputedStyle(document.body).fontSize").removesuffix("px"))
    page.reload()
    expect(page.locator("#dashboard-page")).to_be_visible()

    assert after >= before * 1.2
    assert float(page.evaluate("getComputedStyle(document.body).fontSize").removesuffix("px")) == after


def test_on_a_phone_with_large_text_nothing_runs_off_the_screen(page, account):
    page.set_viewport_size({"width": 375, "height": 740})
    page.click("#text-size")

    for name in ("dashboard", "progress", "account"):
        page.click(f".nav-item[data-page='{name}']")
        overflow = page.evaluate("""() => [...document.querySelectorAll('body *')]
            .filter((e) => e.offsetParent !== null && e.getBoundingClientRect().right > window.innerWidth + 1)
            .map((e) => e.id || e.className || e.tagName)""")
        assert overflow == [], (name, overflow)


def test_answer_options_are_readable_in_both_themes_even_under_the_pointer(page, account):
    start_session(page)
    for theme in ("light", "dark"):
        if theme == "dark":
            page.click("#theme-toggle")
        for index in range(page.locator("#exercise-options .option-btn").count()):
            selector = f"#exercise-options .option-btn:nth-child({index + 1})"
            for hovered in (False, True):
                if hovered:
                    page.hover(selector)
                else:
                    page.mouse.move(0, 0)
                for _ in range(25):  # colors change with a short transition
                    ratio = page.evaluate(CONTRAST, selector)
                    if ratio >= 4.5:
                        break
                    page.wait_for_timeout(200)
                assert ratio >= 4.5, (theme, index, "hovered" if hovered else "resting", ratio)
