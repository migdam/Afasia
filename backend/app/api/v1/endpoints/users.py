"""User profile and progress endpoints."""
import time
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from ....db.database import get_db
from ....db.models import (
    User, TherapySession, Exercise, Progress, UserBadge,
    ScheduledSession, AudioRecording, LoginCutoff
)
from ....core.config import settings
from ....core import login_limit
from ....core.security import (
    create_access_token, get_current_user_id, get_password_hash, security, verify_password,
)
from .auth import login_response
from ..schemas import (
    PasswordChange, TokenResponse, UserResponse, UserUpdate, ProgressResponse, ProgressStats,
    BadgeResponse, ScheduledSessionCreate, ScheduledSessionResponse,
    AudioRecordingResponse
)
import os
import csv
import io
import uuid
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

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

    user.updated_at = datetime.utcnow()

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
    cutoff_date = datetime.utcnow() - timedelta(days=days)
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
        current_streak=user.current_streak,
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
        ScheduledSession.scheduled_time >= datetime.utcnow()
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
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Export progress data as CSV."""
    progress_records = db.query(Progress).filter(
        Progress.user_id == user_id
    ).order_by(Progress.date.desc()).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Date', 'Exercises Completed', 'Accuracy Rate (%)',
        'Time (seconds)', 'Points Earned', 'Difficulty', 'Exercise Type'
    ])

    # Write data
    for record in progress_records:
        writer.writerow([
            record.date.strftime('%Y-%m-%d %H:%M:%S'),
            record.exercises_completed,
            round(record.accuracy_rate, 2),
            record.total_time_seconds,
            record.points_earned,
            record.difficulty_level.value if record.difficulty_level else '',
            record.exercise_type.value if record.exercise_type else ''
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=progress_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


@router.get("/progress/export/pdf")
def export_progress_pdf(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Export progress report as PDF."""
    user = db.query(User).filter(User.id == user_id).first()
    progress_records = db.query(Progress).filter(
        Progress.user_id == user_id
    ).order_by(Progress.date.desc()).limit(10).all()

    # Create PDF in memory
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "Aphasia Therapy Progress Report")

    # User info
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"User: {user.username}")
    c.drawString(50, height - 100, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Stats
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 140, "Overall Statistics")

    c.setFont("Helvetica", 12)
    y = height - 170
    c.drawString(50, y, f"Total Points: {user.total_points}")
    y -= 20
    c.drawString(50, y, f"Current Streak: {user.current_streak} days")
    y -= 20
    c.drawString(50, y, f"Longest Streak: {user.longest_streak} days")
    y -= 40

    # Recent progress
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Recent Progress (Last 10 Sessions)")
    y -= 30

    c.setFont("Helvetica", 10)
    for record in progress_records:
        text = f"{record.date.strftime('%Y-%m-%d')}: {record.exercises_completed} exercises, {round(record.accuracy_rate, 1)}% accuracy, {record.points_earned} points"
        c.drawString(50, y, text)
        y -= 20

        if y < 50:  # New page if needed
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=progress_report_{datetime.now().strftime('%Y%m%d')}.pdf"}
    )


@router.post("/audio/upload", response_model=AudioRecordingResponse)
async def upload_audio(
    exercise_id: int,
    audio: UploadFile = File(...),
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
