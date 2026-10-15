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


MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December"],
    "pl": ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia",
           "września", "października", "listopada", "grudnia"],
}


def date_in_words(moment: datetime, zone_name: Optional[str], language: str) -> str:
    """A (naive UTC) time's date in the person's time zone, in words, such as
    "3 marca 2026"."""
    local = as_utc(moment).astimezone(zone(zone_name))
    return f"{local.day} {MONTHS[language][local.month - 1]} {local.year}"


# Counts in words, by plural category: the web app uses the same forms
# (frontend/js/i18n.js).
COUNTS = {
    "day": {"en": {"one": "{n} day", "other": "{n} days"},
            "pl": {"one": "{n} dzień", "few": "{n} dni", "many": "{n} dni"}},
    "exercise": {"en": {"one": "{n} exercise", "other": "{n} exercises"},
                 "pl": {"one": "{n} ćwiczenie", "few": "{n} ćwiczenia", "many": "{n} ćwiczeń"}},
    "point": {"en": {"one": "{n} point", "other": "{n} points"},
              "pl": {"one": "{n} punkt", "few": "{n} punkty", "many": "{n} punktów"}},
}


def plural_category(n: int, language: str) -> str:
    """The plural category of a whole number (Unicode CLDR's rules)."""
    if language == "pl":
        if n == 1:
            return "one"
        if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
            return "few"
        return "many"
    return "one" if n == 1 else "other"


def count(n: int, unit: str, language: str) -> str:
    """A whole number with its unit in the right form: "1 dzień", "2 dni", "5 dni"."""
    return COUNTS[unit][language][plural_category(n, language)].format(n=n)
