"""The words and formats of the progress exports, in English and Polish
(backlog P2-10c). The web app's own texts are in frontend/js/i18n.js; these
are for the files people download and may give to their therapist."""
from datetime import datetime
from typing import Optional

from .core.clock import as_utc
from .streaks import zone

LANGUAGES = ("en", "pl")

TEXTS = {
    "en": {
        "csv_headers": ["Date ({zone})", "Exercises", "Accuracy (%)", "Time (seconds)", "Points",
                        "Level", "Exercise type"],
        "levels": {"easy": "Easy", "medium": "Medium", "hard": "Hard"},
        "types": {"word_naming": "Word Naming", "sentence_completion": "Sentence Completion",
                  "pronunciation": "Pronunciation", "image_recognition": "Image Recognition"},
    },
    "pl": {
        "csv_headers": ["Data ({zone})", "Ćwiczenia", "Trafność (%)", "Czas (sekundy)", "Punkty",
                        "Poziom", "Rodzaj ćwiczeń"],
        "levels": {"easy": "Łatwy", "medium": "Średni", "hard": "Trudny"},
        "types": {"word_naming": "Nazywanie słów", "sentence_completion": "Uzupełnianie zdań",
                  "pronunciation": "Wymowa", "image_recognition": "Rozpoznawanie obrazów"},
    },
}

# Spreadsheet programs set to Polish expect semicolons between values and
# decimal commas; set to English, commas and decimal points.
CSV_DELIMITER = {"en": ",", "pl": ";"}


def language_of(*choices: Optional[str]) -> str:
    """The first known language among the choices; English otherwise."""
    return next((choice for choice in choices if choice in LANGUAGES), "en")


def decimal(value: float, language: str) -> str:
    """A number with up to two decimals, written as the language does:
    66.67 in English, 66,67 in Polish."""
    text = f"{round(value, 2):g}"
    return text.replace(".", ",") if language == "pl" else text


def local_time(moment: datetime, zone_name: Optional[str]) -> str:
    """A (naive UTC) time in the person's time zone, such as 2026-03-03 00:30."""
    return as_utc(moment).astimezone(zone(zone_name)).strftime("%Y-%m-%d %H:%M")
