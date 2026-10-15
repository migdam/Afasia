"""The frontend never builds HTML from strings (backlog P1-1)."""
import re
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def test_no_html_built_from_strings_or_inline_handlers():
    found = [
        f"{path.name}:{number}"
        for path in sorted((FRONTEND / "js").glob("*.js"))
        for number, line in enumerate(path.read_text().splitlines(), 1)
        if re.search(r"\.(innerHTML|outerHTML)\s*=|insertAdjacentHTML|\son[a-z]+=", line)
    ]

    assert not found, f"use textContent and DOM methods instead: {found}"


def test_index_html_has_no_inline_scripts_or_handlers():
    html = (FRONTEND / "index.html").read_text()

    assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html), "inline <script>"
    assert not re.search(r"\son[a-z]+=", html), "inline event handler"


def test_the_page_policy_allows_no_other_websites():
    html = (FRONTEND / "index.html").read_text()
    policy = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', html).group(1)
    connect = next(d for d in policy.split(";") if d.strip().startswith("connect-src")).split()[1:]

    assert "http:" not in connect and "https:" not in connect and "*" not in connect, connect
