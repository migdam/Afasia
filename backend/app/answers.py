"""Forgiving answer checks (loop/PROMPT.md, U6; backlog P2-5).

Typing is hard after a stroke, so an answer is compared with the expected
one after normalizing both: case, extra spaces and punctuation don't count,
and neither do Polish letters typed without their marks ("lozko" for
"łóżko"). A near miss (a letter or two out) is still wrong, but is called
"almost", so the feedback can say so kindly. Whether near misses should
also earn credit is a question for clinical review.
"""
import re
import unicodedata

# Letters that Unicode doesn't split into a base letter and a mark.
NO_MARKS = str.maketrans({"ł": "l", "Ł": "L", "ø": "o", "đ": "d"})


def normalize(text: str) -> str:
    """Lowercase, without accents or punctuation, single-spaced."""
    text = unicodedata.normalize("NFKD", text.translate(NO_MARKS))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return " ".join(text.split())


def matches(given: str, expected: set[str]) -> bool:
    """Whether an answer matches any of the expected ones, once normalized."""
    return normalize(given) in {normalize(e) for e in expected}


def edit_distance(a: str, b: str) -> int:
    """Letters to add, remove, change or swap with a neighbour to turn a into b
    (optimal string alignment distance)."""
    rows = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        rows[i][0] = i
    for j in range(len(b) + 1):
        rows[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            rows[i][j] = min(rows[i - 1][j] + 1, rows[i][j - 1] + 1, rows[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                rows[i][j] = min(rows[i][j], rows[i - 2][j - 2] + 1)
    return rows[-1][-1]


def is_near_miss(given: str, expected: str) -> bool:
    """A wrong answer close enough to call "almost": one slip in a word of up
    to 6 letters, two in a longer one. Answers under 3 letters are too short
    to guess at, and a match isn't a miss."""
    a, b = normalize(given), normalize(expected)
    if a == b or len(a) < 3 or len(b) < 3:
        return False
    allowed = 1 if len(b) <= 6 else 2
    return edit_distance(a, b) <= allowed
