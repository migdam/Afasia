"""The progress report as a PDF, in the person's language, with dates in
their time zone (backlog P2-10c2). It uses DejaVu Sans, embedded, because
the PDF's built-in fonts have no Polish letters such as "ł" (app/fonts/)."""
import io
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .core.clock import as_utc
from .export_text import TEXTS, count, date_in_words, decimal
from .streaks import zone

FONT = "DejaVuSans"
FONT_FILE = Path(__file__).resolve().parent / "fonts" / "DejaVuSans.ttf"
SIZES = {"title": 22, "heading": 15, "text": 12, "small": 10}
MARGIN = 50

REPORT = {
    "en": {
        "title": "Progress report",
        "user": "User: {name}",
        "made": "Made on {date} at {time} ({zone})",
        "overall": "Overall",
        "points": "Points: {points}",
        "streak": "Current streak: {days}",
        "longest": "Longest streak: {days}",
        "recent": "Recent sessions",
        "none": "No finished sessions yet.",
        "session": "{date}: {type} ({level}). {exercises}, {accuracy}% right, {points}.",
        "note": "These are results of practice in the app, not a clinical assessment.",
    },
    "pl": {
        "title": "Raport postępów",
        "user": "Użytkownik: {name}",
        "made": "Utworzono {date} o {time} ({zone})",
        "overall": "Podsumowanie",
        "points": "Punkty: {points}",
        "streak": "Obecna seria: {days}",
        "longest": "Najdłuższa seria: {days}",
        "recent": "Ostatnie sesje",
        "none": "Nie ma jeszcze ukończonych sesji.",
        "session": "{date}: {type} ({level}). {exercises}, {accuracy}% poprawnie, {points}.",
        "note": "To wyniki ćwiczeń w aplikacji, a nie ocena kliniczna.",
    },
}


def report_lines(user, records, language: str, zone_name, now) -> list:
    """The report as (style, text) lines: the person, their totals and their
    recent sessions, newest first."""
    words, names = REPORT[language], TEXTS[language]
    made = as_utc(now).astimezone(zone(zone_name))
    lines = [
        ("title", words["title"]),
        ("text", words["user"].format(name=user.username)),
        ("text", words["made"].format(date=date_in_words(now, zone_name, language),
                                      time=made.strftime("%H:%M"), zone=zone_name or "UTC")),
        ("heading", words["overall"]),
        ("text", words["points"].format(points=user.total_points)),
        ("text", words["streak"].format(days=count(user.streak_now, "day", language))),
        ("text", words["longest"].format(days=count(user.longest_streak, "day", language))),
        ("heading", words["recent"]),
    ]
    if not records:
        lines.append(("text", words["none"]))
    for record in records:
        lines.append(("text", words["session"].format(
            date=date_in_words(record.date, zone_name, language),
            type=names["types"].get(record.exercise_type.value, "") if record.exercise_type else "",
            level=names["levels"].get(record.difficulty_level.value, "").lower() if record.difficulty_level else "",
            exercises=count(record.exercises_completed, "exercise", language),
            accuracy=decimal(round(record.accuracy_rate, 1), language),
            points=count(record.points_earned, "point", language),
        )))
    lines.append(("small", words["note"]))
    return lines


def report_pdf(lines) -> bytes:
    """Lay the lines out on A4 pages, wrapping long ones, with 1.5 line spacing."""
    if FONT not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT, FONT_FILE))
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=A4)
    page.setTitle(lines[0][1])
    width, height = A4
    y = height - MARGIN
    for style, text in lines:
        size = SIZES[style]
        if style in ("heading", "small"):
            y -= size  # space above a heading and the closing note
        for part in simpleSplit(text, FONT, size, width - 2 * MARGIN):
            if y - size < MARGIN:
                page.showPage()
                y = height - MARGIN
            page.setFont(FONT, size)
            page.drawString(MARGIN, y - size, part)
            y -= size * 1.5
    page.save()
    return buffer.getvalue()
