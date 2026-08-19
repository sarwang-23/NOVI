from datetime import datetime, date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.weekly_checkin import WeeklyCheckin

router = APIRouter(
    prefix="/api/v1/checkins",
    tags=["Weekly Check-ins"]
)

# --- SCHEMAS ---

class CheckinCreate(BaseModel):
    week_start: date
    week_end: date
    accomplishments: str | None = None
    learnings: str | None = None
    difficulties: str | None = None
    proud_of: str | None = None
    improvement_area: str | None = None
    mood: str | None = None

class CheckinUpdate(BaseModel):
    accomplishments: str | None = None
    learnings: str | None = None
    difficulties: str | None = None
    proud_of: str | None = None
    improvement_area: str | None = None
    mood: str | None = None
    completed: bool | None = None


# --- HELPER ---

def _get_student(user, db: Session) -> Student:
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student

# --- ENDPOINTS ---

@router.get("")
def get_checkins(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    checkins = db.query(WeeklyCheckin).filter(WeeklyCheckin.student_id == student.id).order_by(WeeklyCheckin.week_start.desc()).all()
    return checkins

@router.get("/current")
def get_current_checkin(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    # Return the most recent incomplete checkin
    checkin = db.query(WeeklyCheckin).filter(
        WeeklyCheckin.student_id == student.id,
        WeeklyCheckin.completed == False
    ).order_by(WeeklyCheckin.week_start.desc()).first()
    
    if not checkin:
        raise HTTPException(status_code=404, detail="No current active check-in found")
        
    return checkin

@router.get("/{checkin_id}")
def get_checkin(checkin_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    checkin = db.query(WeeklyCheckin).filter(
        WeeklyCheckin.id == checkin_id,
        WeeklyCheckin.student_id == student.id
    ).first()
    
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
        
    return checkin

@router.post("")
def create_checkin(payload: CheckinCreate, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    
    # Ensure no exact duplicate week checkin exists
    existing = db.query(WeeklyCheckin).filter(
        WeeklyCheckin.student_id == student.id,
        WeeklyCheckin.week_start == payload.week_start
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="A check-in for this week already exists")
        
    checkin = WeeklyCheckin(
        student_id=student.id,
        week_start=payload.week_start,
        week_end=payload.week_end,
        accomplishments=payload.accomplishments,
        learnings=payload.learnings,
        difficulties=payload.difficulties,
        proud_of=payload.proud_of,
        improvement_area=payload.improvement_area,
        mood=payload.mood
    )
    
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin

@router.put("/{checkin_id}")
def update_checkin(checkin_id: int, payload: CheckinUpdate, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    checkin = db.query(WeeklyCheckin).filter(
        WeeklyCheckin.id == checkin_id,
        WeeklyCheckin.student_id == student.id
    ).first()
    
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(checkin, key, value)
        
    db.commit()
    db.refresh(checkin)
    return checkin
