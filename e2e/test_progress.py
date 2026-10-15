"""The progress page's chart."""
from conftest import call_api
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
    token = page.evaluate("localStorage.getItem('access_token')")
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
