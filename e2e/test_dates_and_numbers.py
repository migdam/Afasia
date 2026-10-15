"""Dates and numbers follow the app's language, not the browser's, with
Polish plural forms from Intl (G9, backlog P2-10b)."""
from datetime import datetime, timezone

from playwright.sync_api import expect

from conftest import browser_token, call_api
from test_session_lists_fit import finish

MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December"],
    "pl": ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia",
           "września", "października", "listopada", "grudnia"],
}


def today(language):
    now = datetime.now(timezone.utc)  # the test browser runs in UTC
    return f"{now.day} {MONTHS[language][now.month - 1]} {now.year}"


def test_dates_are_in_words_in_the_chosen_language_and_follow_a_change(page, servers, account):
    token = browser_token(page)
    finish(servers, token, "pronunciation", "easy", "said_it")
    call_api(servers, "POST", "/users/scheduled-sessions", {
        "title": "Plan", "scheduled_time": "2099-01-01T10:00:00",
        "exercise_type": "word_naming", "difficulty": "easy",
    }, token)
    page.reload()

    expect(page.locator("#scheduled-list")).to_contain_text("1 January 2099")
    expect(page.locator("#scheduled-list")).to_contain_text("10:00")
    expect(page.locator("#recent-sessions")).to_contain_text(today("en"))

    page.click("#lang-toggle")  # Polski: the lists change at once

    expect(page.locator("#scheduled-list")).to_contain_text("1 stycznia 2099")
    expect(page.locator("#recent-sessions")).to_contain_text(today("pl"))


def test_progress_numbers_have_their_units_in_words(page, servers, account):
    finish(servers, browser_token(page), "pronunciation", "easy", "said_it")
    page.reload()
    page.click(".bottom-nav [data-page='progress']")

    expect(page.locator("#progress-longest-streak")).to_have_text("1 day")
    expect(page.locator("#progress-total-time")).to_have_text("0 minutes")  # answered at once
    expect(page.locator("#progress-avg-accuracy")).to_have_text("100%")

    page.click("#lang-toggle")  # Polski

    expect(page.locator("#progress-longest-streak")).to_have_text("1 dzień")
    expect(page.locator("#progress-total-time")).to_have_text("0 minut")
    expect(page.locator(".badge-date")).to_have_text(today("pl"))


def test_polish_plural_forms(page):
    page.click("#lang-toggle")  # Polski

    days = page.evaluate("() => [0, 1, 2, 5, 12, 22].map((n) => i18n.formatCount(n, 'day'))")
    hours = page.evaluate("() => [1, 1.04, 1.5, 2, 5].map((n) => i18n.formatCount(n, 'hour', 1))")

    durations = page.evaluate("() => [1 / 60, 0.05, 0.25, 1.5].map((h) => i18n.formatDuration(h))")

    assert days == ["0 dni", "1 dzień", "2 dni", "5 dni", "12 dni", "22 dni"]
    assert hours == ["1 godzina", "1 godzina", "1,5 godziny", "2 godziny", "5 godzin"]
    assert durations == ["1 minuta", "3 minuty", "15 minut", "1,5 godziny"]


def test_english_plural_forms(page):
    days = page.evaluate("() => [0, 1, 2].map((n) => i18n.formatCount(n, 'day'))")
    hours = page.evaluate("() => [1, 1.5].map((n) => i18n.formatCount(n, 'hour', 1))")

    assert days == ["0 days", "1 day", "2 days"]
    assert hours == ["1 hour", "1.5 hours"]
