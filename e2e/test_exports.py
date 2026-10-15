"""Exports download in the language on screen (backlog P2-10c)."""
from pathlib import Path

from conftest import browser_token
from test_session_lists_fit import finish


def test_the_csv_download_is_in_the_language_on_screen(page, servers, account):
    finish(servers, browser_token(page), "pronunciation", "easy", "said_it")
    page.click("#lang-toggle")  # Polski; the account itself stays English
    page.click(".bottom-nav [data-page='progress']")

    with page.expect_download() as download:
        page.click("#export-csv")

    lines = Path(download.value.path()).read_text(encoding="utf-8-sig").splitlines()
    assert lines[0].startswith("Data (") and lines[0].endswith(";Poziom;Rodzaj ćwiczeń")
    assert lines[1].endswith(";Łatwy;Wymowa")
