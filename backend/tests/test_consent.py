"""Consent to recording and to speech recognition, kept on the server (P1-6b1)."""
from test_recordings import WEBM, an_exercise_of, register, upload


def consents(client, auth):
    return client.get("/api/v1/users/consents", headers=auth)


def answer(client, auth, **choices):
    return client.put("/api/v1/users/consents", headers=auth, json=choices)


def test_a_new_account_has_not_been_asked_yet(client):
    pat = register(client, "pat")

    assert consents(client, pat).json() == {"recordings": None, "speech_recognition": None}


def test_each_answer_is_kept_on_its_own(client):
    pat = register(client, "pat")

    assert answer(client, pat, recordings=True).status_code == 200
    assert consents(client, pat).json() == {"recordings": True, "speech_recognition": None}

    answer(client, pat, speech_recognition=False)
    assert consents(client, pat).json() == {"recordings": True, "speech_recognition": False}


def test_answers_are_yes_or_no_about_known_things(client):
    pat = register(client, "pat")

    assert answer(client, pat, recordings="maybe").status_code == 422
    assert answer(client, pat, location=True).status_code == 422
    assert consents(client, pat).json() == {"recordings": None, "speech_recognition": None}


def test_recordings_are_refused_without_consent(client):
    pat = register(client, "pat")
    exercise = an_exercise_of(client, pat)

    assert upload(client, pat, exercise).status_code == 403  # never asked
    answer(client, pat, recordings=True)
    assert upload(client, pat, exercise, WEBM).status_code == 200
    answer(client, pat, recordings=False)  # changed their mind
    assert upload(client, pat, exercise).status_code == 403


def test_answers_belong_to_one_person(client):
    pat, sam = register(client, "pat"), register(client, "sam")

    answer(client, pat, recordings=True, speech_recognition=True)

    assert consents(client, sam).json() == {"recordings": None, "speech_recognition": None}
