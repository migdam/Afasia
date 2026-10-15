"""The CSV export is in the person's language, with times in their time zone
and numbers as their spreadsheet program expects (backlog P2-10c)."""
import csv
import io
from datetime import datetime

from app.api.v1.endpoints import therapy
from test_recordings import register

FINISHED = datetime(2026, 3, 2, 23, 30)  # UTC: 00:30 on 3 March in Warsaw


def practise(client, auth, monkeypatch, ratings=("said_it",), difficulty="easy"):
    """Finish a pronunciation session, rating each exercise in turn."""
    monkeypatch.setattr(therapy, "utcnow", lambda: FINISHED)
    session = client.post("/api/v1/therapy/sessions", headers=auth, json={
        "title": "t", "exercise_type": "pronunciation", "difficulty": difficulty,
        "num_exercises": len(ratings),
    }).json()
    exercises = client.get(f"/api/v1/therapy/sessions/{session['id']}/exercises", headers=auth).json()
    for exercise, rating in zip(exercises, ratings):
        client.post(f"/api/v1/therapy/exercises/{exercise['id']}/answer", headers=auth,
                    json={"answer": "", "time_taken_seconds": 3, "self_rating": rating})


def table(response, delimiter):
    assert response.status_code == 200
    text = response.content.decode("utf-8")
    assert text.startswith("﻿")  # so spreadsheet programs read Polish letters
    return list(csv.reader(io.StringIO(text[1:]), delimiter=delimiter))


def test_in_polish_with_local_times_and_decimal_commas(client, monkeypatch):
    pat = register(client, "pat")
    client.put("/api/v1/users/time-zone", headers=pat, json={"time_zone": "Europe/Warsaw"})
    practise(client, pat, monkeypatch, ("said_it", "said_it", "not_yet"), difficulty="medium")

    header, row = table(client.get("/api/v1/users/progress/export/csv?lang=pl", headers=pat), ";")

    assert header == ["Data (Europe/Warsaw)", "Ćwiczenia", "Trafność (%)", "Czas (sekundy)", "Punkty",
                      "Poziom", "Rodzaj ćwiczeń"]
    assert row[:3] == ["2026-03-03 00:30", "3", "66,67"]
    assert row[5:] == ["Średni", "Wymowa"]


def test_in_english_by_default_and_in_utc_when_the_zone_is_unknown(client, monkeypatch):
    pat = register(client, "pat")
    practise(client, pat, monkeypatch, ("said_it", "said_it", "not_yet"))

    header, row = table(client.get("/api/v1/users/progress/export/csv", headers=pat), ",")

    assert header == ["Date (UTC)", "Exercises", "Accuracy (%)", "Time (seconds)", "Points",
                      "Level", "Exercise type"]
    assert row[:3] == ["2026-03-02 23:30", "3", "66.67"]
    assert row[5:] == ["Easy", "Pronunciation"]


def test_the_account_language_counts_when_none_is_asked_for(client, monkeypatch):
    pat = register(client, "pat")
    client.put("/api/v1/users/profile", headers=pat, json={"language": "pl"})
    practise(client, pat, monkeypatch)

    header, row = table(client.get("/api/v1/users/progress/export/csv", headers=pat), ";")

    assert header[0] == "Data (UTC)"
    assert row[2] == "100"


def test_only_known_languages(client):
    pat = register(client, "pat")

    assert client.get("/api/v1/users/progress/export/csv?lang=de", headers=pat).status_code == 422
