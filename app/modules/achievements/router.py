from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.achievement import Achievement

router = APIRouter(
    prefix="/api/v1/achievements",
    tags=["Achievements"]
)

class AchievementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=100)
    organization: str | None = Field(default=None, max_length=255)
    achievement_date: datetime | None = None
    skills: str | None = Field(default=None, max_length=2000)

class AchievementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=100)
    organization: str | None = Field(default=None, max_length=255)
    achievement_date: datetime | None = None
    skills: str | None = Field(default=None, max_length=2000)

def _get_student(user, db: Session) -> Student:
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student

def _serialize_achievement(achievement: Achievement):
    return {
        "id": achievement.id,
        "student_id": achievement.student_id,
        "title": achievement.title,
        "description": achievement.description,
        "category": achievement.category,
        "organization": achievement.organization,
        "achievement_date": achievement.achievement_date,
        "skills": achievement.skills,
        "created_at": achievement.created_at
    }

@router.get("/me")
def get_my_achievements(
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    achievements = db.query(Achievement).filter(
        Achievement.student_id == student.id
    ).all()
    
    return [_serialize_achievement(a) for a in achievements]

@router.post("/me", status_code=201)
def create_achievement(
    payload: AchievementCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    achievement = Achievement(
        student_id=student.id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        organization=payload.organization,
        achievement_date=payload.achievement_date,
        skills=payload.skills
    )

    db.add(achievement)
    db.commit()
    db.refresh(achievement)

    return _serialize_achievement(achievement)

@router.patch("/{achievement_id}")
def update_achievement(
    achievement_id: int,
    payload: AchievementUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    achievement = db.query(Achievement).filter(
        Achievement.id == achievement_id,
        Achievement.student_id == student.id
    ).first()

    if not achievement:
        raise HTTPException(
            status_code=404,
            detail="Achievement not found"
        )

    if payload.title is not None:
        achievement.title = payload.title

    if payload.description is not None:
        achievement.description = payload.description

    if payload.category is not None:
        achievement.category = payload.category

    if payload.organization is not None:
        achievement.organization = payload.organization

    if payload.achievement_date is not None:
        achievement.achievement_date = payload.achievement_date

    if payload.skills is not None:
        achievement.skills = payload.skills

    db.commit()
    db.refresh(achievement)

    return _serialize_achievement(achievement)

@router.get("/{achievement_id}")
def get_achievement(
    achievement_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    achievement = db.query(Achievement).filter(
        Achievement.id == achievement_id,
        Achievement.student_id == student.id
    ).first()

    if not achievement:
        raise HTTPException(
            status_code=404,
            detail="Achievement not found"
        )

    return _serialize_achievement(achievement)
