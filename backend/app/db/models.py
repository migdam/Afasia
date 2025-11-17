"""Database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from .database import Base


class DifficultyLevel(str, enum.Enum):
    """Exercise difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ExerciseType(str, enum.Enum):
    """Types of therapy exercises."""
    WORD_NAMING = "word_naming"
    SENTENCE_COMPLETION = "sentence_completion"
    IMAGE_RECOGNITION = "image_recognition"
    PRONUNCIATION = "pronunciation"


class UserRole(str, enum.Enum):
    """User roles."""
    PATIENT = "patient"
    THERAPIST = "therapist"
    ADMIN = "admin"


class BadgeType(str, enum.Enum):
    """Achievement badge types."""
    FIRST_SESSION = "first_session"
    WEEK_STREAK = "week_streak"
    MONTH_STREAK = "month_streak"
    PERFECTIONIST = "perfectionist"
    DEDICATED = "dedicated"
    MASTER = "master"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    language = Column(String, default="en")  # en or pl
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Gamification
    total_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime)

    # Relationships
    sessions = relationship("TherapySession", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    scheduled_sessions = relationship("ScheduledSession", back_populates="user", cascade="all, delete-orphan")
    audio_recordings = relationship("AudioRecording", back_populates="user", cascade="all, delete-orphan")


class TherapySession(Base):
    """Therapy session model."""
    __tablename__ = "therapy_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    exercise_type = Column(Enum(ExerciseType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    language = Column(String, default="en")
    total_exercises = Column(Integer, default=0)
    completed_exercises = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    duration_seconds = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    is_completed = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="sessions")
    exercises = relationship("Exercise", back_populates="session", cascade="all, delete-orphan")


class Exercise(Base):
    """Individual exercise within a session."""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("therapy_sessions.id"), nullable=False)
    exercise_type = Column(Enum(ExerciseType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    question = Column(Text, nullable=False)
    correct_answer = Column(String, nullable=False)
    user_answer = Column(String)
    image_url = Column(String)  # For image-based exercises
    audio_url = Column(String)  # For pronunciation exercises
    options = Column(JSON)  # Multiple choice options
    is_correct = Column(Boolean)
    time_taken_seconds = Column(Integer)
    attempts = Column(Integer, default=0)
    completed_at = Column(DateTime)

    # Relationships
    session = relationship("TherapySession", back_populates="exercises")


class Progress(Base):
    """User progress tracking."""
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    exercises_completed = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    total_time_seconds = Column(Integer, default=0)
    points_earned = Column(Integer, default=0)
    difficulty_level = Column(Enum(DifficultyLevel))
    exercise_type = Column(Enum(ExerciseType))

    # Relationships
    user = relationship("User", back_populates="progress_records")


class UserBadge(Base):
    """User achievement badges."""
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_type = Column(Enum(BadgeType), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)  # Additional badge information

    # Relationships
    user = relationship("User", back_populates="badges")


class ScheduledSession(Base):
    """Scheduled therapy sessions with reminders."""
    __tablename__ = "scheduled_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    exercise_type = Column(Enum(ExerciseType))
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    is_completed = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="scheduled_sessions")


class AudioRecording(Base):
    """Audio recordings for pronunciation practice."""
    __tablename__ = "audio_recordings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    file_path = Column(String, nullable=False)
    duration_seconds = Column(Float)
    transcription = Column(Text)  # Speech-to-text result
    accuracy_score = Column(Float)  # Pronunciation accuracy
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audio_recordings")
