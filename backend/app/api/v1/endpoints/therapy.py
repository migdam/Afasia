"""Therapy session and exercise endpoints."""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from ....db.database import get_db
from ....db.models import (
    User, TherapySession, Exercise, Progress, UserBadge,
    DifficultyLevel, ExerciseType, BadgeType, ExerciseCue, ExerciseChoice, ExerciseTiles
)
from ....answers import is_near_miss, matches
from ....content import MAX_CUE_LEVEL, accepted_answers, choice_words, content_items, letter_tiles, naming_cue
from ....core.clock import utcnow
from ....core.security import get_current_user_id
from ..schemas import (
    SessionCreate, SessionResponse,
    ExerciseResponse, ExerciseAnswer, AnswerResult, BadgeResponse, Hint, Choices, Tiles
)
import random

router = APIRouter()


# Exercise content lives in backend/content/ (app/content.py), in Polish and
# English, pending clinical review (loop/PROMPT.md, C7). It is read and
# checked here, when the app starts. EXERCISE_DATA is the English view of it,
# listing every type that has content; sessions use their own language
# (generate_exercises). Image recognition has none until there are pictures
# (backlog H2).
EXERCISE_DATA = {
    exercise_type: {d: content_items(exercise_type, d, "en") for d in DifficultyLevel}
    for exercise_type in ExerciseType
    if content_items(exercise_type, DifficultyLevel.EASY, "en") is not None
}


def generate_exercises(
    exercise_type: ExerciseType, difficulty: DifficultyLevel, count: int, language: str = "en",
) -> List[dict]:
    """Pick random exercises of a type and difficulty, repeating items if needed.

    Raises LookupError when there is no content for that type and difficulty,
    rather than substituting another difficulty or looping forever.
    """
    available = content_items(exercise_type, difficulty, language)
    if available is None:  # no content file for this type (tests may add items)
        available = EXERCISE_DATA.get(exercise_type, {}).get(difficulty, [])
    if not available:
        raise LookupError(f"no {exercise_type.value} exercises at {difficulty.value} difficulty")

    # Repeat if needed
    exercises = []
    while len(exercises) < count:
        exercises.extend(random.sample(available, min(len(available), count - len(exercises))))

    # A fresh order of options for every exercise, so where the right one
    # sits gives nothing away.
    return [
        {**item, "options": random.sample(item["options"], len(item["options"]))} if item.get("options") else item
        for item in exercises[:count]
    ]


# The share of an exercise's points kept after 0, 1, 2 or 3 naming hints, so
# finding a word on one's own counts most. Placeholder values, pending
# clinical review (loop/PROMPT.md, C3, C7).
HINT_POINT_SHARE = (1.0, 0.75, 0.5, 0.25)
# The most an answer chosen from a list, or built from its own letters, can
# keep: both are easier than recalling the word. Placeholder, pending
# clinical review.
CHOICE_POINT_SHARE = 0.5


def calculate_points(
    difficulty: DifficultyLevel, is_correct: bool, cue_level: int = 0,
    choices_shown: bool = False, tiles_used: bool = False,
) -> int:
    """Points for an answer: by difficulty, less for each hint used or for
    choosing from a list or building it from letter tiles."""
    if not is_correct:
        return 0

    points_map = {
        DifficultyLevel.EASY: 10,
        DifficultyLevel.MEDIUM: 20,
        DifficultyLevel.HARD: 30,
    }
    share = HINT_POINT_SHARE[min(cue_level, MAX_CUE_LEVEL)]
    if choices_shown or tiles_used:
        share = min(share, CHOICE_POINT_SHARE)
    return round(points_map.get(difficulty, 10) * share)


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
    now = utcnow()
    correct_count = sum(1 for e in session.exercises if e.is_correct)
    points = sum(
        calculate_points(e.difficulty, e.is_correct, e.cue_level, e.choices_shown, e.tiles_used)
        for e in session.exercises
    )

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
            session_data.num_exercises,
            session_data.language,
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


@router.post("/exercises/{exercise_id}/hint", response_model=Hint)
def next_hint(
    exercise_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """The next naming hint: 1 the meaning, 2 the first letter, 3 the word.

    The level reached is kept with the exercise, and the points for a right
    answer go down with each hint (calculate_points).
    """
    exercise = db.query(Exercise).join(TherapySession).filter(
        Exercise.id == exercise_id, TherapySession.user_id == user_id,
    ).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    if exercise.exercise_type != ExerciseType.WORD_NAMING:
        raise HTTPException(status_code=422, detail="Only naming exercises have hints")
    if exercise.is_correct is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This exercise has been answered")
    if exercise.cue_level >= MAX_CUE_LEVEL:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="There are no more hints")

    level = exercise.cue_level + 1
    if exercise.cue:
        exercise.cue.level = level
    else:
        exercise.cue = ExerciseCue(level=level)
    db.commit()
    return Hint(
        level=level,
        cue=naming_cue(exercise.session.language, exercise.correct_answer, level),
        last=level == MAX_CUE_LEVEL,
    )


@router.post("/exercises/{exercise_id}/choices", response_model=Choices)
def word_choices(
    exercise_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Words to choose from instead of typing (U6): the answer and three
    others, in the session's language. Recorded, as choosing is easier than
    recalling (calculate_points); asking again gives the same words."""
    exercise = db.query(Exercise).join(TherapySession).filter(
        Exercise.id == exercise_id, TherapySession.user_id == user_id,
    ).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    if exercise.exercise_type != ExerciseType.WORD_NAMING:
        raise HTTPException(status_code=422, detail="Only naming exercises offer words to choose from")
    if exercise.is_correct is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This exercise has been answered")
    if not exercise.choice:
        exercise.choice = ExerciseChoice(words=choice_words(exercise.session.language, exercise.correct_answer))
        db.commit()
    return Choices(choices=exercise.choice.words)


@router.post("/exercises/{exercise_id}/tiles", response_model=Tiles)
def word_tiles(
    exercise_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """The answer's letters, shuffled, to build the word without typing (U6).
    Recorded, as it is easier than recalling (calculate_points); asking again
    gives the same order."""
    exercise = db.query(Exercise).join(TherapySession).filter(
        Exercise.id == exercise_id, TherapySession.user_id == user_id,
    ).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    if exercise.exercise_type != ExerciseType.WORD_NAMING:
        raise HTTPException(status_code=422, detail="Only naming exercises offer letter tiles")
    if exercise.is_correct is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This exercise has been answered")
    if not exercise.tiles:
        exercise.tiles = ExerciseTiles(letters=letter_tiles(exercise.correct_answer))
        db.commit()
    return Tiles(tiles=exercise.tiles.letters)


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
    # Forgiving: case, spacing, punctuation and missing Polish letters don't
    # count (app/answers.py). Naming also takes the word's synonyms.
    if exercise.exercise_type == ExerciseType.WORD_NAMING:
        expected = accepted_answers(session.language, exercise.correct_answer.strip())
    else:
        expected = {exercise.correct_answer}
    is_correct = matches(answer_data.answer, expected)
    if exercise.exercise_type == ExerciseType.PRONUNCIATION and answer_data.self_rating:
        # Speech recognition is unreliable for aphasic speech (C5), so the
        # person's own rating decides; what it heard is only kept.
        is_correct = answer_data.self_rating == "said_it"
    almost = not answer_data.self_rating and not is_correct and exercise.exercise_type != ExerciseType.SENTENCE_COMPLETION and any(
        is_near_miss(answer_data.answer, e) for e in expected
    )

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
        Exercise.completed_at: utcnow(),
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

    result = AnswerResult.model_validate(exercise)
    result.almost = almost
    return result


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
