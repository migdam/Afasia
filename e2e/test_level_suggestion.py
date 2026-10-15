"""The dashboard suggests another level; the person decides (P2-8c)."""
from playwright.sync_api import expect

from conftest import browser_token, call_api


def finish_sessions(servers, page, count, right=True, difficulty="easy"):
    token = browser_token(page)
    for _ in range(count):
        _, session = call_api(servers, "POST", "/therapy/sessions", {
            "title": "t", "exercise_type": "pronunciation", "difficulty": difficulty, "num_exercises": 1,
        }, token)
        _, exercises = call_api(servers, "GET", f"/therapy/sessions/{session['id']}/exercises", token=token)
        call_api(servers, "POST", f"/therapy/exercises/{exercises[0]['id']}/answer", {
            "answer": "", "time_taken_seconds": 3, "self_rating": "said_it" if right else "not_yet",
        }, token)


def choose(page, exercise_type, difficulty):
    page.select_option("#exercise-type", exercise_type)
    page.select_option("#difficulty", difficulty)


def test_after_good_sessions_a_harder_level_is_offered_and_taken_only_on_request(page, servers, account):
    finish_sessions(servers, page, 3)
    page.reload()
    choose(page, "pronunciation", "easy")

    suggestion = page.locator("#level-suggestion")
    expect(suggestion).to_be_visible()
    expect(page.locator("#level-suggestion-text")).to_have_text(
        "Your last sessions at this level went well. You could try a harder level.")
    expect(page.locator("#difficulty")).to_have_value("easy")  # nothing changes by itself

    page.click("#level-suggestion-accept")

    expect(page.locator("#difficulty")).to_have_value("medium")
    expect(suggestion).to_be_hidden()


def test_the_suggestion_is_in_polish_and_only_where_it_applies(page, servers, account):
    finish_sessions(servers, page, 3, right=False, difficulty="medium")
    page.reload()
    page.click("#lang-toggle")  # Polski
    choose(page, "pronunciation", "medium")

    expect(page.locator("#level-suggestion-text")).to_have_text(
        "Ostatnie sesje na tym poziomie były trudne. Łatwiejszy poziom może na razie pomóc.")
    expect(page.locator("#level-suggestion-accept")).to_have_text("Przełącz na: Łatwy")

    choose(page, "word_naming", "medium")  # another type: nothing to suggest
    expect(page.locator("#level-suggestion")).to_be_hidden()


def test_a_new_account_gets_no_suggestion(page, account):
    expect(page.locator("#level-suggestion")).to_be_hidden()
