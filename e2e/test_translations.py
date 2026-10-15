"""Every text the app shows comes from its dictionaries, which have the same
keys in English and Polish (G9, backlog P2-10a)."""
import re
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
I18N = (FRONTEND / "js" / "i18n.js").read_text()
SCRIPTS = "\n".join(path.read_text() for path in sorted((FRONTEND / "js").glob("*.js")))
PAGE = (FRONTEND / "index.html").read_text()

# Where the scripts name a dictionary key: in a call, an attribute or a map.
KEY_PATTERNS = (
    r"""translate\(\s*['"](\w+)['"]""",
    r"""notify\(\s*['"](\w+)['"]""",
    r"""showEmpty\([^,]+,\s*['"](\w+)['"]""",
    r"""showFormMessage\([^,]+,\s*['"](\w+)['"]""",
    r"""translated\([^)]*?['"](\w+)['"]\)""",
    r"""dataset\.i18n\s*=\s*['"](\w+)['"]""",
)


def keys(language):
    block = re.search(rf"^    {language}: \{{(.*?)^    \}}", I18N, re.S | re.M).group(1)
    return set(re.findall(r"^\s+(\w+):", block, re.M))


def used_keys():
    used = set(re.findall(r'data-i18n(?:-label|-alt)?="(\w+)"', PAGE))
    for pattern in KEY_PATTERNS:
        used |= set(re.findall(pattern, SCRIPTS))
    for table in re.findall(r"const \w+_KEYS = \{(.*?)\};", SCRIPTS, re.S):
        used |= set(re.findall(r":\s*'(\w+)'", table))
    return used


def test_english_and_polish_have_the_same_keys():
    english, polish = keys("en"), keys("pl")

    assert english and english == polish, english ^ polish


def test_every_key_the_app_asks_for_is_in_the_dictionaries():
    used = used_keys()

    assert {"stop", "badgeWeekStreak", "wordNaming", "appName"} <= used  # the patterns see them
    assert not used - keys("en"), used - keys("en")


def test_no_english_left_in_the_scripts():
    # Texts that were once written into the scripts instead of the dictionaries.
    left = [text for text in ("No data available", "'Recording", "'Completed'", "'Activate'",
                              "'Deactivate'", "Points:", "'Stop'") if text in SCRIPTS]

    assert not left, left
