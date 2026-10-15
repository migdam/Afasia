"""Therapy session and exercise endpoints."""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from ....db.database import get_db
from ....db.models import (
    User, TherapySession, Exercise, Progress, UserBadge,
    DifficultyLevel, ExerciseType, BadgeType
)
from ....core.security import get_current_user_id
from ..schemas import (
    SessionCreate, SessionResponse,
    ExerciseResponse, ExerciseAnswer, AnswerResult, BadgeResponse
)
import random

router = APIRouter()


# Sample exercise data: placeholder items, pending clinical review
# (loop/PROMPT.md, C7). A prompt must not contain its answer, except in
# repetition (pronunciation); tests/test_content.py checks this.
EXERCISE_DATA = {
    # There are no pictures or recordings yet (backlog H2, H3), so items have
    # no "image" or "audio"; any added must exist under frontend/
    # (tests/test_content.py). Naming items describe the thing to name; once
    # there are pictures, show the picture alone and offer the description
    # as the first hint (backlog P2-3).
    ExerciseType.WORD_NAMING: {
        DifficultyLevel.EASY: [
            {"question": "What is it? A small pet that purrs and says meow.", "answer": "cat"},
            {"question": "What is it? A pet that barks and wags its tail.", "answer": "dog"},
            {"question": "What is it? A building where a family lives.", "answer": "house"},
            {"question": "What is it? You drive it on the road. It has four wheels.", "answer": "car"},
            {"question": "What is it? A tall plant with a trunk, branches and leaves.", "answer": "tree"},
        ],
        DifficultyLevel.MEDIUM: [
            {"question": "What is it? It has two wheels and pedals. You ride it.", "answer": "bicycle"},
            {"question": "What is it? A small computer that folds shut.", "answer": "laptop"},
            {"question": "What is it? You use it to call people and talk to them.", "answer": "telephone"},
        ],
        DifficultyLevel.HARD: [
            {"question": "What is it? A doctor puts it in their ears to listen to your heart.", "answer": "stethoscope"},
            {"question": "What is it? A flower with many thin petals that blooms in autumn.", "answer": "chrysanthemum"},
        ],
    },
    ExerciseType.SENTENCE_COMPLETION: {
        DifficultyLevel.EASY: [
            {"question": "The sky is ___", "answer": "blue", "options": ["blue", "green", "red", "yellow"]},
            {"question": "I am ___", "answer": "happy", "options": ["happy", "table", "run", "cold"]},
            {"question": "The sun is ___", "answer": "bright", "options": ["bright", "dark", "soft", "loud"]},
        ],
        DifficultyLevel.MEDIUM: [
            {"question": "She went to the ___ to buy groceries", "answer": "store", "options": ["store", "park", "beach", "school"]},
            {"question": "The ___ is barking loudly", "answer": "dog", "options": ["cat", "dog", "bird", "fish"]},
        ],
        DifficultyLevel.HARD: [
            {"question": "The physician prescribed ___ for the infection", "answer": "antibiotics", "options": ["antibiotics", "vitamins", "exercise", "rest"]},
        ],
    },
    ExerciseType.PRONUNCIATION: {
        DifficultyLevel.EASY: [
            {"question": "Say: Hello", "answer": "hello"},
            {"question": "Say: Thank you", "answer": "thank you"},
        ],
        DifficultyLevel.MEDIUM: [
            {"question": "Say: Beautiful", "answer": "beautiful"},
            {"question": "Say: Wonderful", "answer": "wonderful"},
        ],
        DifficultyLevel.HARD: [
            {"question": "Say: Extraordinary", "answer": "extraordinary"},
        ],
    },
}


def generate_exercises(exercise_type: ExerciseType, difficulty: DifficultyLevel, count: int) -> List[dict]:
    """Pick random exercises of a type and difficulty, repeating items if needed.

    Raises LookupError when there is no content for that type and difficulty,
    rather than substituting another difficulty or looping forever.
    """
    available = EXERCISE_DATA.get(exercise_type, {}).get(difficulty, [])
    if not available:
        raise LookupError(f"no {exercise_type.value} exercises at {difficulty.value} difficulty")

    # Repeat if needed
    exercises = []
    while len(exercises) < count:
        exercises.extend(random.sample(available, min(len(available), count - len(exercises))))

    return exercises[:count]


def calculate_points(difficulty: DifficultyLevel, is_correct: bool) -> int:
    """Calculate points based on difficulty and correctness."""
    if not is_correct:
        return 0

    points_map = {
        DifficultyLevel.EASY: 10,
        DifficultyLevel.MEDIUM: 20,
        DifficultyLevel.HARD: 30,
    }
    return points_map.get(difficulty, 10)


def check_and_award_badges(db: Session, user: User):
    """Check if user earned any new badges."""
    new_badges = []

    # First session badge
    if user.sessions and len(user.sessions) == 1:
        if not db.query(UserBadge).filter(
            UserBadge.user_id == user.id,
            UserBadge.badge_type == BadgeType.FIRST_SESSION
        ).first():
            badge = UserBadge(user_id=user.id, badge_type=BadgeType.FIRST_SESSION)
            db.add(badge)
            new_badges.append(badge)

    # Week streak badge
    if user.current_streak >= 7:
        if not db.query(UserBadge).filter(
            UserBadge.user_id == user.id,
            UserBadge.badge_type == BadgeType.WEEK_STREAK
        ).first():
            badge = UserBadge(user_id=user.id, badge_type=BadgeType.WEEK_STREAK)
            db.add(badge)
            new_badges.append(badge)

    # Month streak badge
    if user.current_streak >= 30:
        if not db.query(UserBadge).filter(
            UserBadge.user_id == user.id,
            UserBadge.badge_type == BadgeType.MONTH_STREAK
        ).first():
            badge = UserBadge(user_id=user.id, badge_type=BadgeType.MONTH_STREAK)
            db.add(badge)
            new_badges.append(badge)

    return new_badges


def finish_session(db: Session, session: TherapySession):
    """Score a session whose exercises are all answered, and credit the user.

    Runs once per session: submit_answer calls it only after atomically
    marking the session completed.
    """
    now = datetime.utcnow()
    correct_count = sum(1 for e in session.exercises if e.is_correct)
    points = sum(calculate_points(e.difficulty, e.is_correct) for e in session.exercises)

    session.is_completed = True
    session.completed_at = now
    session.score = (correct_count / session.total_exercises) * 100
    session.duration_seconds = int((now - session.started_at).total_seconds())

    # Update user stats
    user = session.user
    # Added in SQL, so sessions finishing at the same moment don't lose points.
    user.total_points = User.total_points + points

    # Update streak
    today = now.date()
    if user.last_activity_date:
        last_date = user.last_activity_date.date()
        if (today - last_date).days == 1:
            user.current_streak += 1
        elif (today - last_date).days > 1:
            user.current_streak = 1
    else:
        user.current_streak = 1

    user.longest_streak = max(user.longest_streak, user.current_streak)
    user.last_activity_date = now

    # Check for badges
    check_and_award_badges(db, user)

    # Create progress record
    progress = Progress(
        user_id=user.id,
        exercises_completed=session.total_exercises,
        accuracy_rate=session.score,
        total_time_seconds=session.duration_seconds,
        points_earned=points,
        difficulty_level=session.difficulty,
        exercise_type=session.exercise_type,
    )
    db.add(progress)


@router.post("/sessions", response_model=SessionResponse)
def create_session(
    session_data: SessionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new therapy session."""
    # Pick the exercises first, so a request without content creates nothing.
    try:
        exercise_templates = generate_exercises(
            session_data.exercise_type,
            session_data.difficulty,
            session_data.num_exercises
        )
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"There are no {session_data.exercise_type.value} exercises "
                   f"at {session_data.difficulty.value} difficulty yet"
        ) from None

    # Create session
    session = TherapySession(
        user_id=user_id,
        title=session_data.title,
        description=session_data.description,
        exercise_type=session_data.exercise_type,
        difficulty=session_data.difficulty,
        language=session_data.language,
        total_exercises=session_data.num_exercises,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    for template in exercise_templates:
        exercise = Exercise(
            session_id=session.id,
            exercise_type=session_data.exercise_type,
            difficulty=session_data.difficulty,
            question=template["question"],
            correct_answer=template["answer"],
            image_url=template.get("image"),
            audio_url=template.get("audio"),
            options=template.get("options"),
        )
        db.add(exercise)

    db.commit()
    db.refresh(session)

    return SessionResponse.model_validate(session)


@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(
    skip: int = 0,
    limit: int = 20,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user's therapy sessions."""
    sessions = db.query(TherapySession).filter(
        TherapySession.user_id == user_id
    ).order_by(TherapySession.started_at.desc()).offset(skip).limit(limit).all()

    return [SessionResponse.model_validate(s) for s in sessions]


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get specific session details."""
    session = db.query(TherapySession).filter(
        TherapySession.id == session_id,
        TherapySession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return SessionResponse.model_validate(session)


@router.get("/sessions/{session_id}/exercises", response_model=List[ExerciseResponse])
def get_exercises(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get exercises for a session."""
    session = db.query(TherapySession).filter(
        TherapySession.id == session_id,
        TherapySession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    exercises = db.query(Exercise).filter(Exercise.session_id == session_id).all()
    return [ExerciseResponse.model_validate(e) for e in exercises]


@router.post("/exercises/{exercise_id}/answer", response_model=AnswerResult)
def submit_answer(
    exercise_id: int,
    answer_data: ExerciseAnswer,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Submit the answer to an exercise. The last answer completes the session."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # Verify user owns this session
    session = db.query(TherapySession).filter(
        TherapySession.id == exercise.session_id,
        TherapySession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check answer
    is_correct = answer_data.answer.lower().strip() == exercise.correct_answer.lower().strip()

    # One answer per exercise, claimed atomically: of two answers sent at the
    # same moment only one can change the exercise from unanswered, so
    # nothing is scored or credited twice. The other gets 409.
    claimed = db.query(Exercise).filter(
        Exercise.id == exercise.id,
        Exercise.is_correct.is_(None)
    ).update({
        Exercise.user_answer: answer_data.answer,
        Exercise.is_correct: is_correct,
        Exercise.time_taken_seconds: answer_data.time_taken_seconds,
        Exercise.attempts: Exercise.attempts + 1,
        Exercise.completed_at: datetime.utcnow(),
    }, synchronize_session=False)
    if not claimed:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Exercise already answered"
        )
    db.commit()

    # Count after committing: whichever of several simultaneous answers
    # commits last sees all of them. Completing is claimed atomically too, so
    # the session is completed and credited exactly once.
    answered = db.query(Exercise).filter(
        Exercise.session_id == session.id,
        Exercise.is_correct.isnot(None)
    ).count()
    db.query(TherapySession).filter(
        TherapySession.id == session.id,
        TherapySession.completed_exercises < answered
    ).update({TherapySession.completed_exercises: answered}, synchronize_session=False)
    if answered == session.total_exercises and db.query(TherapySession).filter(
        TherapySession.id == session.id,
        TherapySession.is_completed.is_(False)
    ).update({TherapySession.is_completed: True}, synchronize_session=False):
        finish_session(db, session)

    db.commit()
    db.refresh(exercise)

    return AnswerResult.model_validate(exercise)


@router.post("/sessions/{session_id}/complete", response_model=SessionResponse)
def complete_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Return a finished session's result.

    The last answer completes and scores the session on the server; a request
    body (the client's own score or duration) is ignored.
    """
    session = db.query(TherapySession).filter(
        TherapySession.id == session_id,
        TherapySession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if not session.is_completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not all exercises have been answered"
        )

    return SessionResponse.model_validate(session)
