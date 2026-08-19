from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.services.dashboard import DashboardService

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
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

@router.get("/me")
def get_dashboard(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    return DashboardService.get_dashboard(student, db)
