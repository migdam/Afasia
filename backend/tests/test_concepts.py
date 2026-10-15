"""Naming content as data, in Polish and English (P2-2a)."""
import json

import pytest

from app.content import CONCEPTS_FILE, ContentError, load_concepts
from app.db.models import DifficultyLevel
from test_recordings import register


def test_the_content_file_has_30_concepts_in_both_languages():
    concepts = load_concepts()

    assert len(concepts) >= 30
    for difficulty in DifficultyLevel:
        assert [c for c in concepts if c.difficulty == difficulty], difficulty
    for language in ("en", "pl"):
        words = [getattr(c, language).word.lower() for c in concepts]
        assert len(words) == len(set(words)), f"{language}: a word is used twice"


def test_every_concept_waits_for_clinical_review():
    assert {c.review for c in load_concepts()} == {"pending"}


def broken_file(tmp_path, change):
    data = json.loads(CONCEPTS_FILE.read_text())
    change(data["concepts"][0])
    path = tmp_path / "concepts.json"
    path.write_text(json.dumps(data, ensure_ascii=False))
    return path


@pytest.mark.parametrize("change", [
    lambda c: c["pl"].update(description=f"To jest {c['pl']['word']}."),         # the answer itself
    lambda c: c["pl"].update(description=f"Mały {c['pl']['word']}ek, miły."),     # an inflected form
    lambda c: c["en"].update(description=f"A {c['en']['synonyms'][0] if c['en']['synonyms'] else c['en']['word']}."),
    lambda c: c.pop("pl"),                                                         # a language missing
    lambda c: c["en"].update(word=""),                                             # an empty word
])
def test_content_that_breaks_the_rules_stops_the_app(tmp_path, change):
    with pytest.raises(ContentError):
        load_concepts(broken_file(tmp_path, change))


def naming(client, auth, language, count=5):
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "word_naming", "difficulty": "easy",
        "language": language, "num_exercises": count,
    })
    assert session.status_code == 200, session.text
    return client.get(f"/api/v1/therapy/sessions/{session.json()['id']}/exercises", headers=auth).json()


def test_naming_comes_in_the_sessions_language(client):
    pat = register(client, "pat")
    by_description = {c.pl.description: c for c in load_concepts()}

    for exercise in naming(client, pat, "pl"):
        assert exercise["question"].startswith("Co to jest?")
        assert exercise["question"].removeprefix("Co to jest? ") in by_description


def test_the_word_or_a_synonym_counts_as_right(client):
    pat = register(client, "pat")
    with_synonym = {c.en.description: c for c in load_concepts() if c.en.synonyms}

    easy = [c for c in load_concepts() if c.difficulty == DifficultyLevel.EASY]
    # Every easy concept, so the ones with synonyms are certainly drawn.
    exercises = naming(client, pat, "en", count=len(easy))
    tried = 0
    for exercise in exercises:
        concept = with_synonym.get(exercise["question"].removeprefix("What is it? "))
        if concept:
            answer = concept.en.synonyms[0].upper()  # any case
            result = client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=pat,
                                 json={"answer": answer, "time_taken_seconds": 2}).json()
            assert result["is_correct"], answer
            tried += 1
    assert tried, "no easy concept has a synonym"


def test_unknown_languages_are_refused(client):
    pat = register(client, "pat")

    response = client.post("/api/v1/therapy/sessions", headers=pat, json={
        "title": "t", "exercise_type": "word_naming", "difficulty": "easy", "language": "de", "num_exercises": 1,
    })

    assert response.status_code == 422
