"""Exercise content kept as data (backlog P2-2), checked when the app starts.

backend/content/concepts.json holds the naming concepts, written natively
in Polish and English. The app refuses to start if the file breaks the
rules below, so bad content never reaches anyone.
"""
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from .db.models import DifficultyLevel

CONCEPTS_FILE = Path(__file__).resolve().parents[1] / "content" / "concepts.json"
LANGUAGES = ("en", "pl")
# How a naming prompt starts, per language.
NAMING_QUESTION = {"en": "What is it?", "pl": "Co to jest?"}


class ContentError(Exception):
    """The content file breaks a rule; the message says which."""


class Features(BaseModel):
    """Semantic features, for Semantic Feature Analysis cues (docs/clinical)."""
    model_config = ConfigDict(extra="forbid")

    category: str = Field(min_length=1)
    use: str = Field(min_length=1)
    location: str = Field(min_length=1)


class Wording(BaseModel):
    """A concept in one language."""
    model_config = ConfigDict(extra="forbid")

    word: str = Field(min_length=1)
    synonyms: list[str] = []
    first_sound: str = Field(min_length=1)
    description: str = Field(min_length=1)
    features: Features

    @property
    def answers(self) -> list[str]:
        return [self.word, *self.synonyms]

    @property
    def first_letter(self) -> str:
        return self.word[0]

    @model_validator(mode="after")
    def description_does_not_give_the_answer(self):
        # C4: no answer in its own prompt. A word that starts with the answer
        # counts too, which catches inflected forms ("kota" for "kot").
        words = re.findall(r"\w+", self.description.lower())
        for answer in self.answers:
            for part in answer.lower().split():
                if len(part) >= 3 and any(w.startswith(part) for w in words):
                    raise ValueError(f"the description gives away {answer!r}")
        return self


class Concept(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z_]+$")
    difficulty: DifficultyLevel
    en: Wording
    pl: Wording
    image: Optional[str] = None  # asset paths, once there are licensed assets (H2, H3)
    audio: Optional[str] = None
    review: Literal["pending", "approved"]


class ContentFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int
    about: str
    concepts: list[Concept]

    @field_validator("concepts")
    @classmethod
    def ids_and_words_are_unique(cls, concepts):
        ids = [c.id for c in concepts]
        if len(ids) != len(set(ids)):
            raise ValueError("a concept id is used twice")
        for language in LANGUAGES:
            words = [getattr(c, language).word.lower() for c in concepts]
            if len(words) != len(set(words)):
                raise ValueError(f"a {language} word is used twice")
        return concepts


def load_concepts(path: Path = CONCEPTS_FILE) -> list[Concept]:
    """Read and check a content file; raises ContentError if it breaks a rule."""
    try:
        return ContentFile.model_validate(json.loads(path.read_text(encoding="utf-8"))).concepts
    except (OSError, ValueError, ValidationError) as error:
        raise ContentError(f"{path}: {error}") from error


@lru_cache(maxsize=1)
def concepts() -> list[Concept]:
    """The app's naming concepts, read once."""
    return load_concepts()


def naming_items(difficulty: DifficultyLevel, language: str) -> list[dict]:
    """Naming exercises for a difficulty, in a language (English if unknown)."""
    language = language if language in LANGUAGES else "en"
    return [
        {
            "question": f"{NAMING_QUESTION[language]} {getattr(c, language).description}",
            "answer": getattr(c, language).word,
        }
        for c in concepts() if c.difficulty == difficulty
    ]


def accepted_answers(language: str, answer: str) -> set[str]:
    """Every answer that counts for a naming answer: the word and its synonyms."""
    language = language if language in LANGUAGES else "en"
    for c in concepts():
        wording = getattr(c, language)
        if wording.word.lower() == answer.lower():
            return {a.lower() for a in wording.answers}
    return {answer.lower()}
