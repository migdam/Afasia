"""The PDF report is in the person's language, with dates in words in their
time zone and Polish plural forms, in an embedded font that has Polish
letters (backlog P2-10c2)."""
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace as Thing

from app.db.models import DifficultyLevel, ExerciseType
from app.export_text import count
from app.progress_report import FONT_FILE, report_lines
from test_csv_export import practise
from test_recordings import register

ROOT = Path(__file__).resolve().parents[2]
PERSON = Thing(username="Łucja", total_points=20, streak_now=3, longest_streak=5)
SESSION = Thing(date=datetime(2026, 3, 2, 23, 30), exercise_type=ExerciseType.PRONUNCIATION,
                difficulty_level=DifficultyLevel.EASY, exercises_completed=3, accuracy_rate=66.666,
                points_earned=20)
NOW = datetime(2026, 3, 3, 9, 15)  # UTC; 10:15 in Warsaw


def texts(language, zone="Europe/Warsaw", sessions=(SESSION,)):
    return [text for _, text in report_lines(PERSON, list(sessions), language, zone, NOW)]


def test_the_report_in_polish_in_the_persons_time_zone():
    assert texts("pl") == [
        "Raport postępów",
        "Użytkownik: Łucja",
        "Utworzono 3 marca 2026 o 10:15 (Europe/Warsaw)",
        "Podsumowanie",
        "Punkty: 20",
        "Obecna seria: 3 dni",
        "Najdłuższa seria: 5 dni",
        "Ostatnie sesje",
        "3 marca 2026: Wymowa (łatwy). 3 ćwiczenia, 66,7% poprawnie, 20 punktów.",
        "To wyniki ćwiczeń w aplikacji, a nie ocena kliniczna.",
    ]


def test_the_report_in_english_in_utc():
    lines = texts("en", zone=None)

    assert lines[2] == "Made on 3 March 2026 at 09:15 (UTC)"
    assert lines[8] == "2 March 2026: Pronunciation (easy). 3 exercises, 66.7% right, 20 points."


def test_without_sessions_the_report_says_so():
    assert "Nie ma jeszcze ukończonych sesji." in texts("pl", sessions=())


def test_polish_plural_forms():
    assert [count(n, "day", "pl") for n in (0, 1, 2, 5, 12, 22, 25)] == [
        "0 dni", "1 dzień", "2 dni", "5 dni", "12 dni", "22 dni", "25 dni"]
    assert [count(n, "exercise", "pl") for n in (1, 2, 5, 12, 22)] == [
        "1 ćwiczenie", "2 ćwiczenia", "5 ćwiczeń", "12 ćwiczeń", "22 ćwiczenia"]
    assert [count(n, "point", "pl") for n in (1, 3, 11, 24, 100)] == [
        "1 punkt", "3 punkty", "11 punktów", "24 punkty", "100 punktów"]
    assert [count(n, "point", "en") for n in (0, 1, 2)] == ["0 points", "1 point", "2 points"]


def test_the_pdf_is_a4_in_an_embedded_font_with_polish_letters(client, monkeypatch):
    pat = register(client, "pat")
    practise(client, pat, monkeypatch)

    response = client.get("/api/v1/users/progress/export/pdf?lang=pl", headers=pat)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert b"DejaVuSans" in response.content  # embedded: the built-in fonts have no "ł"
    assert b"595.2756 841.8898" in response.content  # A4, in points


def test_only_known_languages(client):
    pat = register(client, "pat")

    assert client.get("/api/v1/users/progress/export/pdf?lang=de", headers=pat).status_code == 422


def test_the_font_comes_with_its_license_and_credit():
    assert FONT_FILE.exists()
    assert "Bitstream" in (FONT_FILE.parent / "LICENSE-DejaVu.txt").read_text()
    assert "DejaVuSans.ttf" in (ROOT / "frontend" / "assets" / "CREDITS.md").read_text()
