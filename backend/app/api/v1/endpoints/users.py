"""User profile and progress endpoints."""
import time
from typing import List, Literal, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, UploadFile, File, Form
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from ....db.database import get_db
from ....db.models import (
    User, TherapySession, Exercise, Progress, UserBadge,
    ScheduledSession, AudioRecording, LoginCutoff, Consent, TimeZoneSetting
)
from ....core.clock import as_utc, utcnow
from ....export_text import CSV_DELIMITER, TEXTS, decimal, language_of, local_time
from ....progress_report import report_lines, report_pdf
from ....core.config import settings
from ....core import login_limit
from ....core.security import (
    clear_login_cookie, create_access_token, get_current_user_id, get_password_hash, security,
    verify_password,
)
from .auth import login_response
from ..schemas import (
    AccountDeletion, Consents, TimeZoneChoice, PasswordChange, TokenResponse, UserResponse, UserUpdate, ProgressResponse, ProgressStats,
    BadgeResponse, ScheduledSessionCreate, ScheduledSessionResponse,
    AudioRecordingResponse
)
import enum
import os
import csv
import io
import uuid
from pathlib import Path

router = APIRouter()

@router.post("/password", response_model=TokenResponse)
def change_password(
    data: PasswordChange,
    request: Request,
    response: Response,
    user_id: int = Depends(get_current_user_id),
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Change your password. Your other logins end; this one gets a new token.

    Wrong current passwords count towards the same limit as logging in, so a
    borrowed login can't be used to guess the password.
    """
    user = db.get(User, user_id)
    client = request.client.host if request.client else "unknown"
    wait = login_limit.retry_after(user.username, client)
    if wait:
        raise login_limit.too_many_attempts(wait)
    if not verify_password(data.current_password, user.hashed_password):
        login_limit.record_failure(user.username, client)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    login_limit.record_success(user.username, client)

    now = int(time.time())
    user.hashed_password = get_password_hash(data.new_password)
    cutoff = db.get(LoginCutoff, user.id) or LoginCutoff(user_id=user.id)
    cutoff.not_before = now
    db.add(cutoff)
    db.commit()
    # As with renewals, through the cookie the new token goes only into the cookie.
    return login_response(response, user, create_access_token(user.id, auth_time=now), show_token=bearer is not None)


CONSENT_KINDS = tuple(Consents.model_fields)


def get_consents(db: Session, user_id: int) -> Consents:
    rows = db.query(Consent).filter(Consent.user_id == user_id).all()
    return Consents(**{row.kind: row.granted for row in rows if row.kind in CONSENT_KINDS})


@router.get("/consents", response_model=Consents)
def read_consents(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Your answers about recordings and speech recognition (null: not asked yet)."""
    return get_consents(db, user_id)


@router.put("/consents", response_model=Consents)
def update_consents(
    choices: Consents,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Give or withdraw consent. Only the kinds in the request change."""
    for kind, granted in choices.model_dump(exclude_unset=True).items():
        if granted is None:
            continue
        row = db.get(Consent, (user_id, kind)) or Consent(user_id=user_id, kind=kind)
        row.granted = granted
        row.updated_at = utcnow()
        db.add(row)
    db.commit()
    return get_consents(db, user_id)


@router.get("/time-zone", response_model=TimeZoneChoice)
def read_time_zone(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    row = db.get(TimeZoneSetting, user_id)
    return TimeZoneChoice(time_zone=row.time_zone if row else None)


@router.put("/time-zone", response_model=TimeZoneChoice)
def update_time_zone(
    choice: TimeZoneChoice,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Your time zone, sent by the browser, so streak days follow your own
    midnight (P2-9b). Null forgets it: days are then counted in UTC."""
    row = db.get(TimeZoneSetting, user_id)
    if choice.time_zone is None:
        if row:
            db.delete(row)
    elif row:
        row.time_zone = choice.time_zone
    else:
        db.add(TimeZoneSetting(user_id=user_id, time_zone=choice.time_zone))
    db.commit()
    return choice


def as_data(row, leave_out=()) -> dict:
    """A database row as plain JSON-ready data, without the columns left out."""
    data = {}
    for column in row.__table__.columns:
        if column.name in leave_out:
            continue
        value = getattr(row, column.name)
        if isinstance(value, datetime):
            value = as_utc(value).isoformat()
        elif isinstance(value, enum.Enum):
            value = value.value
        data[column.name] = value
    return data


@router.get("/me/export")
def export_my_data(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Everything stored about you, as one JSON file to download.

    Left out: the password hash, and where recordings sit on the server's
    disk (each recording can be played through GET /users/audio/{id}).
    """
    user = db.get(User, user_id)
    data = {
        "exported_at": as_utc(utcnow()).isoformat(),
        "account": as_data(user, leave_out={"hashed_password"}),
        "consents": get_consents(db, user_id).model_dump(),
        "time_zone": read_time_zone(user_id, db).time_zone,
        "sessions": [
            {**as_data(session), "exercises": [
                {**as_data(e), "cue_level": e.cue_level, "choices_shown": e.choices_shown,
                 "tiles_used": e.tiles_used}
                for e in session.exercises
            ]}
            for session in user.sessions
        ],
        "progress": [as_data(p) for p in user.progress_records],
        "badges": [as_data(b) for b in user.badges],
        "scheduled_sessions": [as_data(s) for s in user.scheduled_sessions],
        "recordings": [
            {**as_data(r, leave_out={"file_path"}), "play_url": f"/api/v1/users/audio/{r.id}"}
            for r in user.audio_recordings
        ],
    }
    return JSONResponse(
        data, headers={"Content-Disposition": 'attachment; filename="afasia-my-data.json"'},
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    data: AccountDeletion,
    request: Request,
    response: Response,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete your account and everything stored about you, recordings included.

    Needs your password; wrong ones count towards the login limit.
    """
    user = db.get(User, user_id)
    client = request.client.host if request.client else "unknown"
    wait = login_limit.retry_after(user.username, client)
    if wait:
        raise login_limit.too_many_attempts(wait)
    if not verify_password(data.password, user.hashed_password):
        login_limit.record_failure(user.username, client)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is incorrect")

    files = [Path(r.file_path) for r in user.audio_recordings]
    # Rows without a foreign key to users go by hand; the rest follow the user.
    db.query(Consent).filter(Consent.user_id == user_id).delete()
    db.query(TimeZoneSetting).filter(TimeZoneSetting.user_id == user_id).delete()
    db.query(LoginCutoff).filter(LoginCutoff.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    for path in files:
        path.unlink(missing_ok=True)
    clear_login_cookie(response)


# Audio formats accepted for recordings, by content type. Browsers record
# WebM (Chrome, Firefox) or MP4 (Safari).
AUDIO_EXTENSIONS = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/mp4": ".m4a",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
}
AUDIO_TYPES = {".webm": "audio/webm", ".ogg": "audio/ogg", ".m4a": "audio/mp4", ".mp3": "audio/mpeg", ".wav": "audio/wav"}


@router.get("/profile", response_model=UserResponse)
def get_profile(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user profile."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    update_data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if update_data.full_name is not None:
        user.full_name = update_data.full_name
    if update_data.language is not None:
        user.language = update_data.language

    user.updated_at = utcnow()

    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


@router.get("/progress", response_model=ProgressStats)
def get_progress(
    days: int = 30,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user progress statistics."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get progress history
    cutoff_date = utcnow() - timedelta(days=days)
    progress_records = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.date >= cutoff_date
    ).order_by(Progress.date.desc()).all()

    # Calculate stats
    total_sessions = db.query(TherapySession).filter(
        TherapySession.user_id == user_id,
        TherapySession.is_completed == True
    ).count()

    total_exercises = db.query(Exercise).join(TherapySession).filter(
        TherapySession.user_id == user_id,
        Exercise.is_correct.isnot(None)
    ).count()

    correct_exercises = db.query(Exercise).join(TherapySession).filter(
        TherapySession.user_id == user_id,
        Exercise.is_correct == True
    ).count()

    average_accuracy = (correct_exercises / total_exercises * 100) if total_exercises > 0 else 0.0

    total_time_seconds = db.query(func.sum(TherapySession.duration_seconds)).filter(
        TherapySession.user_id == user_id,
        TherapySession.is_completed == True
    ).scalar() or 0

    return ProgressStats(
        total_sessions=total_sessions,
        total_exercises=total_exercises,
        average_accuracy=round(average_accuracy, 2),
        total_time_hours=round(total_time_seconds / 3600, 2),
        total_points=user.total_points,
        current_streak=user.streak_now,
        longest_streak=user.longest_streak,
        progress_history=[ProgressResponse.model_validate(p) for p in progress_records]
    )


@router.get("/badges", response_model=List[BadgeResponse])
def get_badges(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user badges."""
    badges = db.query(UserBadge).filter(
        UserBadge.user_id == user_id
    ).order_by(UserBadge.earned_at.desc()).all()

    return [BadgeResponse.model_validate(b) for b in badges]


@router.get("/scheduled-sessions", response_model=List[ScheduledSessionResponse])
def get_scheduled_sessions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user's scheduled sessions."""
    sessions = db.query(ScheduledSession).filter(
        ScheduledSession.user_id == user_id,
        ScheduledSession.scheduled_time >= utcnow()
    ).order_by(ScheduledSession.scheduled_time).all()

    return [ScheduledSessionResponse.model_validate(s) for s in sessions]


@router.post("/scheduled-sessions", response_model=ScheduledSessionResponse)
def create_scheduled_session(
    session_data: ScheduledSessionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Schedule a new therapy session."""
    scheduled = ScheduledSession(
        user_id=user_id,
        scheduled_time=session_data.scheduled_time,
        title=session_data.title,
        description=session_data.description,
        exercise_type=session_data.exercise_type,
        difficulty=session_data.difficulty,
    )

    db.add(scheduled)
    db.commit()
    db.refresh(scheduled)

    return ScheduledSessionResponse.model_validate(scheduled)


@router.delete("/scheduled-sessions/{session_id}")
def delete_scheduled_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a scheduled session."""
    session = db.query(ScheduledSession).filter(
        ScheduledSession.id == session_id,
        ScheduledSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled session not found"
        )

    db.delete(session)
    db.commit()

    return {"message": "Scheduled session deleted"}


@router.get("/progress/export/csv")
def export_progress_csv(
    lang: Optional[Literal["en", "pl"]] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Every finished session as a spreadsheet file, in the language asked
    for (or the account's), with times in your time zone (backlog P2-10c)."""
    user = db.get(User, user_id)
    language = language_of(lang, user.language)
    words = TEXTS[language]
    setting = db.get(TimeZoneSetting, user_id)
    zone_name = setting.time_zone if setting else None
    progress_records = db.query(Progress).filter(
        Progress.user_id == user_id
    ).order_by(Progress.date.desc()).all()

    output = io.StringIO()
    # A byte-order mark, so spreadsheet programs read Polish letters as UTF-8.
    output.write("\ufeff")
    writer = csv.writer(output, delimiter=CSV_DELIMITER[language])
    header = list(words["csv_headers"])
    header[0] = header[0].format(zone=zone_name or "UTC")
    writer.writerow(header)
    for record in progress_records:
        writer.writerow([
            local_time(record.date, zone_name),
            record.exercises_completed,
            decimal(record.accuracy_rate, language),
            record.total_time_seconds,
            record.points_earned,
            words["levels"].get(record.difficulty_level.value, "") if record.difficulty_level else "",
            words["types"].get(record.exercise_type.value, "") if record.exercise_type else "",
        ])

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=progress_{utcnow().strftime('%Y%m%d')}.csv"}
    )


@router.get("/progress/export/pdf")
def export_progress_pdf(
    lang: Optional[Literal["en", "pl"]] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """A short progress report as a PDF (A4), in the language asked for (or
    the account's), with dates in your time zone (backlog P2-10c2)."""
    user = db.get(User, user_id)
    setting = db.get(TimeZoneSetting, user_id)
    progress_records = db.query(Progress).filter(
        Progress.user_id == user_id
    ).order_by(Progress.date.desc()).limit(10).all()

    lines = report_lines(user, progress_records, language_of(lang, user.language),
                         setting.time_zone if setting else None, utcnow())
    return Response(
        content=report_pdf(lines),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=progress_report_{utcnow().strftime('%Y%m%d')}.pdf"}
    )


@router.post("/audio/upload", response_model=AudioRecordingResponse)
async def upload_audio(
    exercise_id: int,
    audio: UploadFile = File(...),
    # What the browser's speech recognition heard, if the person allowed it.
    transcription: Optional[str] = Form(None, max_length=500),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Upload a recording for one of your own pronunciation exercises."""
    exercise = db.query(Exercise).join(TherapySession).filter(
        Exercise.id == exercise_id,
        TherapySession.user_id == user_id
    ).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    if not get_consents(db, user_id).recordings:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not agreed to keeping recordings"
        )

    content_type = (audio.content_type or "").split(";")[0].strip().lower()
    extension = AUDIO_EXTENSIONS.get(content_type)
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload an audio recording"
        )

    # Read at most one byte past the limit, so a huge upload isn't held in memory.
    content = await audio.read(settings.MAX_UPLOAD_SIZE + 1)
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Recording is too large"
        )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recording is empty"
        )

    # A random name, saying nothing about the user or exercise, in a
    # directory that is never served directly.
    directory = Path(settings.UPLOAD_DIR) / "audio"
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / f"{uuid.uuid4().hex}{extension}"
    file_path.write_bytes(content)

    recording = AudioRecording(
        user_id=user_id,
        exercise_id=exercise_id,
        file_path=str(file_path),
        transcription=transcription,
    )

    db.add(recording)
    db.commit()
    db.refresh(recording)

    return AudioRecordingResponse.model_validate(recording)


@router.get("/audio/{recording_id}")
def get_audio_recording(
    recording_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Play one of your own recordings."""
    recording = db.query(AudioRecording).filter(
        AudioRecording.id == recording_id,
        AudioRecording.user_id == user_id
    ).first()

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if not os.path.exists(recording.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )

    media_type = AUDIO_TYPES.get(Path(recording.file_path).suffix, "application/octet-stream")
    return FileResponse(recording.file_path, media_type=media_type)
