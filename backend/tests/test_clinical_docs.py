"""The clinical foundation documents (P2-1, C1, C6, C7)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EN = ROOT / "docs" / "clinical" / "README.md"
PL = ROOT / "docs" / "clinical" / "README.pl.md"
DOI = re.compile(r"doi\.org/(10\.\S+?)[)\s]")


def test_both_languages_exist_and_are_marked_pending_review():
    assert "pending clinical review" in EN.read_text().lower()
    assert "oczekuje na ocenę kliniczną" in PL.read_text().lower()


def test_both_languages_cite_the_same_sources():
    en, pl = set(DOI.findall(EN.read_text())), set(DOI.findall(PL.read_text()))

    assert en and en == pl, en ^ pl


def test_every_exercise_type_the_app_offers_is_covered():
    from app.db.models import ExerciseType

    for doc in (EN, PL):
        text = doc.read_text()
        for exercise_type in ExerciseType:
            assert f"`{exercise_type.value}`" in text, (doc.name, exercise_type.value)


def test_no_efficacy_claims():
    for doc in (EN, PL):
        text = doc.read_text().lower()
        for claim in ("proven", "clinically validated", "udowodnion", "potwierdzona klinicznie"):
            assert claim not in text, (doc.name, claim)
