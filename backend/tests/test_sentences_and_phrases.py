"""Sentence completion and repetition as data, in Polish and English (P2-2b)."""
import json

import pytest

from app.content import PHRASES_FILE, SENTENCES_FILE, ContentError, load_phrases, load_sentences
from app.db.models import DifficultyLevel
from test_recordings import register


def test_both_files_cover_every_difficulty_in_both_languages_and_wait_for_review():
    for items, at_least in ((load_sentences(), 12), (load_phrases(), 9)):
        assert len(items) >= at_least
        assert {i.difficulty for i in items} == set(DifficultyLevel)
        assert {i.review for i in items} == {"pending"}
        for item in items:
            assert item.en and item.pl


def broken(tmp_path, source, change):
    data = json.loads(source.read_text())
    change(data["items"][0])
    path = tmp_path / source.name
    path.write_text(json.dumps(data, ensure_ascii=False))
    return path


@pytest.mark.parametrize("change", [
    lambda i: i["pl"].update(sentence=i["pl"]["sentence"].replace("___", "")),        # no gap
    lambda i: i["pl"].update(sentence=i["pl"]["sentence"] + " ___"),                   # two gaps
    lambda i: i["pl"].update(options=[o for o in i["pl"]["options"] if o != i["pl"]["answer"]] + ["inne"]),
    lambda i: i["en"].update(options=[i["en"]["answer"]] * 4),                         # options repeat
    lambda i: i["en"].update(sentence=f"{i['en']['answer']} ... ___"),                 # gives the answer away
    lambda i: i.pop("en"),
])
def test_sentences_that_break_the_rules_stop_the_app(tmp_path, change):
    with pytest.raises(ContentError):
        load_sentences(broken(tmp_path, SENTENCES_FILE, change))


@pytest.mark.parametrize("change", [lambda i: i["pl"].update(phrase=""), lambda i: i.pop("pl")])
def test_phrases_that_break_the_rules_stop_the_app(tmp_path, change):
    with pytest.raises(ContentError):
        load_phrases(broken(tmp_path, PHRASES_FILE, change))


def session(client, auth, exercise_type, language, difficulty="easy", count=10):
    created = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": exercise_type, "difficulty": difficulty,
        "language": language, "num_exercises": count,
    }).json()
    return client.get(f"/api/v1/therapy/sessions/{created['id']}/exercises", headers=auth).json()


def test_sentence_completion_comes_in_polish(client):
    pat = register(client, "pat")
    polish = {i.pl.sentence for i in load_sentences()}

    assert all(e["question"] in polish for e in session(client, pat, "sentence_completion", "pl"))


def test_the_right_option_is_not_always_in_the_same_place(client):
    pat = register(client, "pat")
    answers = {i.en.sentence: i.en.answer for i in load_sentences()}

    places = {e["options"].index(answers[e["question"]]) for e in session(client, pat, "sentence_completion", "en", count=40)}

    assert len(places) > 1  # 40 shuffles all landing on one place: about 1 in 10^23


def test_repetition_comes_in_polish_and_says_what_to_say(client):
    pat = register(client, "pat")

    for exercise in session(client, pat, "pronunciation", "pl"):
        assert exercise["question"].startswith("Powiedz: ")
