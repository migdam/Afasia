"""The progress page's chart."""
import re

from conftest import browser_token, call_api
from playwright.sync_api import expect
from test_sessions import ANSWERS


def complete_perfect_session(servers, token):
    status, session = call_api(
        servers, "POST", "/therapy/sessions",
        {"title": "Practice", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": 5},
        token,
    )
    assert status == 200
    _, exercises = call_api(servers, "GET", f"/therapy/sessions/{session['id']}/exercises", token=token)
    for exercise in exercises:
        call_api(
            servers, "POST", f"/therapy/exercises/{exercise['id']}/answer",
            {"answer": ANSWERS[exercise["question"]], "time_taken_seconds": 3}, token,
        )


def test_the_chart_draws_a_line_in_the_theme_colour(page, servers, account):
    token = browser_token(page)
    complete_perfect_session(servers, token)
    complete_perfect_session(servers, token)
    page.click("#theme-toggle")  # dark theme

    page.click(".nav-item[data-page='progress']")
    expect(page.locator("#progress-total-sessions")).to_have_text("2")

    box = page.locator("#progress-chart").bounding_box()
    assert box["height"] >= 250
    # Both points are at 100%, so the line between them runs along the top
    # of the plot (50 px padding); sample its midpoint.
    pixel = page.evaluate(
        """() => {
            const canvas = document.getElementById('progress-chart');
            const scale = canvas.width / canvas.getBoundingClientRect().width;
            const x = Math.round(canvas.width / 2), y = Math.round(50 * scale);
            return Array.from(canvas.getContext('2d').getImageData(x, y, 1, 1).data);
        }"""
    )
    primary = page.evaluate(
        "getComputedStyle(document.body).getPropertyValue('--primary-color').trim()"
    )
    assert primary.lower() == "#6366f1"  # the dark theme's primary colour
    assert pixel == [0x63, 0x66, 0xF1, 255]


# What the chart writes on the canvas, recorded as it draws (P2-11).
RECORD_CANVAS_TEXT = """
window.__drawnText = [];
const fillText = CanvasRenderingContext2D.prototype.fillText;
CanvasRenderingContext2D.prototype.fillText = function (text, ...rest) {
    window.__drawnText.push(String(text));
    return fillText.call(this, text, ...rest);
};
"""


def complete_session(servers, token, right):
    """A 5-exercise sentence session with `right` answers right."""
    _, session = call_api(
        servers, "POST", "/therapy/sessions",
        {"title": "Practice", "exercise_type": "sentence_completion", "difficulty": "easy", "num_exercises": 5},
        token,
    )
    _, exercises = call_api(servers, "GET", f"/therapy/sessions/{session['id']}/exercises", token=token)
    for number, exercise in enumerate(exercises):
        answer = ANSWERS[exercise["question"]] if number < right else "zzz"
        call_api(servers, "POST", f"/therapy/exercises/{exercise['id']}/answer",
                 {"answer": answer, "time_taken_seconds": 3}, token)


def test_the_scale_runs_from_0_to_100_percent(page, servers, account):
    complete_session(servers, browser_token(page), right=4)  # 80%: the top would be 80 if it scaled to the data
    page.add_init_script(RECORD_CANVAS_TEXT)
    page.reload()

    page.click(".nav-item[data-page='progress']")
    expect(page.locator("#progress-total-sessions")).to_have_text("1")

    drawn = page.evaluate("window.__drawnText")
    assert ["0%", "20%", "40%", "60%", "80%", "100%"] == [text for text in drawn if text.endswith("%")]


def test_the_chart_has_a_name_and_its_numbers_are_in_a_table(page, servers, account):
    token = browser_token(page)
    complete_session(servers, token, right=4)
    complete_session(servers, token, right=5)
    page.click("#lang-toggle")  # Polski

    page.click(".nav-item[data-page='progress']")

    chart = page.locator("#progress-chart")
    expect(chart).to_have_attribute("role", "img")
    expect(chart).to_have_attribute("aria-label", re.compile("^Wykres liniowy Twoich wyników"))
    page.click("#progress-table-box summary")  # "Pokaż liczby"
    rows = page.locator("#progress-table tbody tr")
    expect(rows).to_have_count(2)
    expect(rows.nth(0).locator("td").nth(1)).to_have_text("80%")  # oldest first, as on the chart
    expect(rows.nth(1).locator("td").nth(1)).to_have_text("100%")
    expect(page.locator("#progress-table th")).to_have_text(["Data", "Wynik"])


def test_with_no_sessions_the_chart_says_so_and_there_is_no_table(page, account):
    page.click(".nav-item[data-page='progress']")

    expect(page.locator("#progress-chart")).to_have_attribute("aria-label", "No results yet.")
    expect(page.locator("#progress-table-box")).to_be_hidden()
