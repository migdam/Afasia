"""Admin endpoints for therapists."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from ....db.database import get_db
from ....db.models import User, TherapySession, Exercise, UserRole
from ....core.security import get_current_user_id
from ..schemas import AdminUserStats, AdminUserResponse, SessionResponse

router = APIRouter()


def get_current_admin(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """Verify current user is admin or therapist."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user or user.role not in [UserRole.ADMIN, UserRole.THERAPIST]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or therapist access required"
        )

    return user


@router.get("/stats", response_model=AdminUserStats)
def get_admin_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get overall platform statistics."""
    total_users = db.query(User).filter(User.role == UserRole.PATIENT).count()
    active_users = db.query(User).filter(
        User.role == UserRole.PATIENT,
        User.is_active == True
    ).count()

    total_sessions = db.query(TherapySession).filter(
        TherapySession.is_completed == True
    ).count()

    total_exercises = db.query(Exercise).filter(
        Exercise.is_correct.isnot(None)
    ).count()

    correct_exercises = db.query(Exercise).filter(
        Exercise.is_correct == True
    ).count()

    average_accuracy = (correct_exercises / total_exercises * 100) if total_exercises > 0 else 0.0

    return AdminUserStats(
        total_users=total_users,
        active_users=active_users,
        total_sessions=total_sessions,
        total_exercises=total_exercises,
        average_accuracy=round(average_accuracy, 2)
    )


@router.get("/users", response_model=List[AdminUserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)."""
    users = db.query(User).filter(
        User.role == UserRole.PATIENT
    ).offset(skip).limit(limit).all()

    return [AdminUserResponse.model_validate(u) for u in users]


@router.get("/users/{user_id}/sessions", response_model=List[SessionResponse])
def get_user_sessions(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get sessions for a specific user (admin only)."""
    sessions = db.query(TherapySession).filter(
        TherapySession.user_id == user_id
    ).order_by(TherapySession.started_at.desc()).offset(skip).limit(limit).all()

    return [SessionResponse.model_validate(s) for s in sessions]


@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Activate a user account."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()

    return {"message": "User activated"}


@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Deactivate a user account."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    db.commit()

    return {"message": "User deactivated"}
