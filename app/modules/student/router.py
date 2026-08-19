from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student

router = APIRouter(
    prefix="/api/v1/students",
    tags=["Students"]
)


class StudentProfileUpdate(BaseModel):
    grade: int | None = Field(default=None, ge=1, le=12)
    school: str | None = Field(default=None, min_length=1, max_length=255)
    curriculum: str | None = Field(default=None, min_length=1, max_length=100)


@router.get("/me")
def get_my_student(
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    auth0_id = user.id

    db_user = db.query(User).filter(
        User.auth0_id == auth0_id
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    student = db.query(Student).filter(
        Student.user_id == db_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    return {
        "id": student.id,
        "user_id": student.user_id,
        "email": db_user.email,
        "role": db_user.role,
        "grade": student.grade,
        "school": student.school,
        "curriculum": student.curriculum
    }


@router.patch("/me")
def update_my_student(
    payload: StudentProfileUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    auth0_id = user.id

    db_user = db.query(User).filter(
        User.auth0_id == auth0_id
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    student = db.query(Student).filter(
        Student.user_id == db_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    if payload.grade is not None:
        student.grade = payload.grade

    if payload.school is not None:
        student.school = payload.school

    if payload.curriculum is not None:
        student.curriculum = payload.curriculum

    db.commit()
    db.refresh(student)

    return {
        "id": student.id,
        "user_id": student.user_id,
        "email": db_user.email,
        "role": db_user.role,
        "grade": student.grade,
        "school": student.school,
        "curriculum": student.curriculum
    }


@router.get("/{student_id}")
def get_student(student_id: int):
    return {
        "id": student_id,
        "message": "Student API is working"
    }
