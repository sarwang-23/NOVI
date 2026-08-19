from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.notification import Notification

router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"]
)

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
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(auth0.get_user), 
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    query = db.query(Notification).filter(Notification.student_id == student.id)
    total = query.count()
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": notifications,
        "skip": skip,
        "limit": limit,
        "total": total
    }

@router.get("/unread")
def get_unread_notifications(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    notifications = db.query(Notification).filter(
        Notification.student_id == student.id,
        Notification.is_read == False
    ).order_by(Notification.created_at.desc()).all()
    return notifications

@router.get("/{notification_id}")
def get_notification(notification_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.student_id == student.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.post("/{notification_id}/read")
def mark_notification_read(notification_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.student_id == student.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification

@router.post("/read-all")
def mark_all_read(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    unread = db.query(Notification).filter(
        Notification.student_id == student.id,
        Notification.is_read == False
    ).all()
    
    now = datetime.utcnow()
    for n in unread:
        n.is_read = True
        n.read_at = now
        
    db.commit()
    return {"message": f"Marked {len(unread)} notifications as read."}

@router.delete("/{notification_id}", status_code=204)
def delete_notification(notification_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.student_id == student.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    db.delete(notification)
    db.commit()
    return None
