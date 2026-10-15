"""Exercise content kept as data (backlog P2-2), checked when the app starts.

backend/content/ holds the exercise content, written natively in Polish and
English: concepts.json (naming), sentences.json (sentence completion) and
phrases.json (repetition). The app refuses to start if a file breaks the
rules below, so bad content never reaches anyone.
"""
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from .db.models import DifficultyLevel

CONTENT = Path(__file__).resolve().parents[1] / "content"
CONCEPTS_FILE = CONTENT / "concepts.json"
SENTENCES_FILE = CONTENT / "sentences.json"
PHRASES_FILE = CONTENT / "phrases.json"
GAP = "___"
LANGUAGES = ("en", "pl")
# How naming and repetition prompts start, per language.
NAMING_QUESTION = {"en": "What is it?", "pl": "Co to jest?"}
SAY = {"en": "Say:", "pl": "Powiedz:"}


class ContentError(Exception):
    """The content file breaks a rule; the message says which."""


def gives_away(text: str, answer: str) -> bool:
    """Whether a text contains an answer, or a word starting with it (C4)."""
    words = re.findall(r"\w+", text.lower())
    return any(
        len(part) >= 3 and any(w.startswith(part) for w in words)
        for part in answer.lower().split()
    )


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
    def prompt_and_first_hint_do_not_give_the_answer(self):
        # C4: no answer in its own prompt, or in the first hint, which shows
        # the features. A word that starts with the answer counts too, which
        # catches inflected forms ("kota" for "kot").
        texts = {"description": self.description, **self.features.model_dump()}
        for name, text in texts.items():
            for answer in self.answers:
                if gives_away(text, answer):
                    raise ValueError(f"the {name} gives away {answer!r}")
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


class SentenceWording(BaseModel):
    """A sentence with one gap, its answer, and four options that all fit
    the gap grammatically; only the answer fits its meaning."""
    model_config = ConfigDict(extra="forbid")

    sentence: str
    answer: str = Field(min_length=1)
    options: list[str] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def one_gap_and_a_fair_choice(self):
        if self.sentence.count(GAP) != 1:
            raise ValueError(f"{self.sentence!r} must have exactly one gap ({GAP})")
        if self.answer not in self.options:
            raise ValueError(f"the answer {self.answer!r} is not among the options")
        if len({o.lower() for o in self.options}) != len(self.options):
            raise ValueError("an option is listed twice")
        if gives_away(self.sentence.replace(GAP, " "), self.answer):
            raise ValueError(f"the sentence gives away {self.answer!r}")
        return self


class SentenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z_]+$")
    difficulty: DifficultyLevel
    en: SentenceWording
    pl: SentenceWording
    review: Literal["pending", "approved"]


class PhraseWording(BaseModel):
    """Something to say, without punctuation, so it compares with what was said."""
    model_config = ConfigDict(extra="forbid")

    phrase: str = Field(min_length=1, pattern=r"^[^.,!?;:]+$")


class PhraseItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z_]+$")
    difficulty: DifficultyLevel
    en: PhraseWording
    pl: PhraseWording
    review: Literal["pending", "approved"]


class ItemFile(BaseModel):
    """sentences.json or phrases.json; the item model is chosen per file."""
    model_config = ConfigDict(extra="forbid")

    version: int
    about: str
    items: list[dict]


def load_items(path: Path, model):
    try:
        raw = ItemFile.model_validate(json.loads(path.read_text(encoding="utf-8")))
        items = [model.model_validate(item) for item in raw.items]
    except (OSError, ValueError, ValidationError) as error:
        raise ContentError(f"{path}: {error}") from error
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        raise ContentError(f"{path}: an id is used twice")
    return items


def load_sentences(path: Path = SENTENCES_FILE) -> list[SentenceItem]:
    return load_items(path, SentenceItem)


def load_phrases(path: Path = PHRASES_FILE) -> list[PhraseItem]:
    return load_items(path, PhraseItem)


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


@lru_cache(maxsize=1)
def sentences() -> list[SentenceItem]:
    return load_sentences()


@lru_cache(maxsize=1)
def phrases() -> list[PhraseItem]:
    return load_phrases()


def known(language: str) -> str:
    return language if language in LANGUAGES else "en"


def naming_items(difficulty: DifficultyLevel, language: str) -> list[dict]:
    """Naming exercises for a difficulty, in a language (English if unknown)."""
    language = known(language)
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


def sentence_items(difficulty: DifficultyLevel, language: str) -> list[dict]:
    language = known(language)
    return [
        {"question": w.sentence, "answer": w.answer, "options": list(w.options)}
        for w in (getattr(i, language) for i in sentences() if i.difficulty == difficulty)
    ]


def phrase_items(difficulty: DifficultyLevel, language: str) -> list[dict]:
    """Repetition: the prompt shows what to say (the C4 exception)."""
    language = known(language)
    items = []
    for item in phrases():
        if item.difficulty == difficulty:
            phrase = getattr(item, language).phrase
            items.append({"question": f"{SAY[language]} {phrase[0].upper()}{phrase[1:]}", "answer": phrase.lower()})
    return items


def content_items(exercise_type, difficulty: DifficultyLevel, language: str):
    """The items for a type, difficulty and language; None for a type that
    has no content file (image recognition, until there are pictures)."""
    from .db.models import ExerciseType

    build = {
        ExerciseType.WORD_NAMING: naming_items,
        ExerciseType.SENTENCE_COMPLETION: sentence_items,
        ExerciseType.PRONUNCIATION: phrase_items,
    }.get(exercise_type)
    return build(difficulty, language) if build else None


# Naming hints, from least to most help (cueing hierarchy, docs/clinical):
# what the thing is for and where it is, then the first letter, then the
# word itself. Plain labels, so no grammar depends on the feature phrases.
CUE_TEMPLATES = {
    "en": (
        "Group: {category}. Used for: {use}. Where: {location}.",
        "It starts with: {letter}",
        "The word is: {word}",
    ),
    "pl": (
        "Grupa: {category}. Do czego: {use}. Gdzie: {location}.",
        "Zaczyna się na: {letter}",
        "To słowo to: {word}",
    ),
}
MAX_CUE_LEVEL = 3


def naming_cue(language: str, word: str, level: int) -> str:
    """The hint at a level (1 to 3) for a naming answer."""
    language = known(language)
    for c in concepts():
        wording = getattr(c, language)
        if wording.word.lower() == word.lower():
            return CUE_TEMPLATES[language][level - 1].format(
                category=wording.features.category, use=wording.features.use,
                location=wording.features.location, letter=wording.first_letter.upper(),
                word=wording.word,
            )
    raise LookupError(f"no concept for {word!r} in {language}")
