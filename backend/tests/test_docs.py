"""The documentation describes only what exists (loop/PROMPT.md, G11)."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = sorted(
    path for path in ROOT.rglob("*.md")
    if not {".venv-check", "node_modules", ".pytest_cache"} & set(path.parts)
)
LINK = re.compile(r"\]\(([^)\s]+)\)")

# Claims that were false when the documentation was checked (backlog P0-9).
# Restore one only together with the check or feature that makes it true.
FALSE_CLAIMS = [
    "production-ready", "production ready", "gotow\\w* do produkcji",
    "wcag 2.1 aa", "lighthouse", "csrf", "rate limit",
    "native speaker", "calendar integration", "integracja z kalendarzem",
    "leaderboard", "ranking", "background sync", "synchronizacja w tle",
    "support@aphasia-therapy.app", "wsparcie@terapia-afazji.app", "@aphasiatherapy",
]
CHECKED_FOR_CLAIMS = ["README.md", "README.pl.md"]


@pytest.mark.parametrize("doc", DOCS, ids=[str(d.relative_to(ROOT)) for d in DOCS])
def test_relative_links_resolve(doc):
    targets = [t.split("#")[0] for t in LINK.findall(doc.read_text()) if "://" not in t and not t.startswith(("#", "mailto:"))]
    missing = [t for t in targets if t and not (doc.parent / t).exists()]

    assert not missing, f"{doc.name} links to missing files: {missing}"


@pytest.mark.parametrize("name", CHECKED_FOR_CLAIMS)
def test_no_known_false_claims(name):
    text = (ROOT / name).read_text().lower()
    found = [claim for claim in FALSE_CLAIMS if re.search(claim, text)]

    assert not found, f"{name} claims: {found}"
