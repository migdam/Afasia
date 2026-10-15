"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, StrictBool, field_validator
from ...db.models import DifficultyLevel, ExerciseType, UserRole, BadgeType


def check_new_password(password: str) -> str:
    """The rules for a new password, at sign-up and when changing it."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    # bcrypt would silently ignore everything past 72 bytes.
    if len(password.encode()) > 72:
        raise ValueError("Password must be at most 72 bytes (UTF-8)")
    return password


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    language: str = "en"

    _password_rules = field_validator("password")(check_new_password)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    _password_rules = field_validator("new_password")(check_new_password)


class Consents(BaseModel):
    """Yes (true), no (false) or not asked yet (null), for each kind of processing.

    recordings: keeping voice recordings on the server.
    speech_recognition: the browser's speech recognition, which may send
    audio to the browser maker's servers.
    """
    model_config = ConfigDict(extra="forbid")

    recordings: Optional[StrictBool] = None
    speech_recognition: Optional[StrictBool] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    language: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    language: str
    role: UserRole
    total_points: int
    current_streak: int
    longest_streak: int
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserResponse(UserResponse):
    """A user as admins and therapists see them, including account status."""
    is_active: bool


class TokenResponse(BaseModel):
    # None when renewing through the login cookie (the cookie carries it).
    access_token: Optional[str]
    token_type: str = "bearer"
    issued_at: int  # Unix time
    expires_at: int  # Unix time
    user: UserResponse


# Exercise schemas
class ExerciseCreate(BaseModel):
    exercise_type: ExerciseType
    difficulty: DifficultyLevel
    question: str
    correct_answer: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    options: Optional[List[str]] = None


class ExerciseResponse(BaseModel):
    id: int
    exercise_type: ExerciseType
    difficulty: DifficultyLevel
    question: str
    image_url: Optional[str]
    audio_url: Optional[str]
    options: Optional[List[str]]
    user_answer: Optional[str]
    is_correct: Optional[bool]
    time_taken_seconds: Optional[int]

    class Config:
        from_attributes = True


class ExerciseAnswer(BaseModel):
    answer: str
    time_taken_seconds: int


class AnswerResult(ExerciseResponse):
    """An answered exercise. Only now is the right answer shown, as feedback."""
    correct_answer: str


# Session schemas
class SessionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    exercise_type: ExerciseType
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    language: str = "en"
    num_exercises: int = 10


class SessionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    exercise_type: ExerciseType
    difficulty: DifficultyLevel
    language: str
    total_exercises: int
    completed_exercises: int
    score: float
    duration_seconds: int
    started_at: datetime
    completed_at: Optional[datetime]
    is_completed: bool

    class Config:
        from_attributes = True


# Progress schemas
class ProgressResponse(BaseModel):
    id: int
    date: datetime
    exercises_completed: int
    accuracy_rate: float
    total_time_seconds: int
    points_earned: int
    difficulty_level: Optional[DifficultyLevel]
    exercise_type: Optional[ExerciseType]

    class Config:
        from_attributes = True


class ProgressStats(BaseModel):
    total_sessions: int
    total_exercises: int
    average_accuracy: float
    total_time_hours: float
    total_points: int
    current_streak: int
    longest_streak: int
    progress_history: List[ProgressResponse]


# Badge schemas
class BadgeResponse(BaseModel):
    id: int
    badge_type: BadgeType
    earned_at: datetime
    details: Optional[dict]

    class Config:
        from_attributes = True


# Scheduled session schemas
class ScheduledSessionCreate(BaseModel):
    scheduled_time: datetime
    title: str
    description: Optional[str] = None
    exercise_type: ExerciseType
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class ScheduledSessionResponse(BaseModel):
    id: int
    scheduled_time: datetime
    title: str
    description: Optional[str]
    exercise_type: ExerciseType
    difficulty: DifficultyLevel
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Audio recording schemas
class AudioRecordingResponse(BaseModel):
    id: int
    duration_seconds: Optional[float]
    transcription: Optional[str]
    accuracy_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# Admin schemas
class AdminUserStats(BaseModel):
    total_users: int
    active_users: int
    total_sessions: int
    total_exercises: int
    average_accuracy: float
