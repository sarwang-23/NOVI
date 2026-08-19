from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.roadmap import Roadmap

router = APIRouter(
    prefix="/api/v1/roadmaps",
    tags=["Roadmaps"]
)


class RoadmapCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    current_grade: int | None = Field(default=None, ge=1, le=12)
    target_grade: int | None = Field(default=None, ge=1, le=12)


class RoadmapUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    current_grade: int | None = Field(default=None, ge=1, le=12)
    target_grade: int | None = Field(default=None, ge=1, le=12)



def _get_student(user, db: Session) -> Student:
    db_user = db.query(User).filter(
        User.auth0_id == user.id
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

    return student


@router.get("/me")
def get_my_roadmap(
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    roadmaps = db.query(Roadmap).filter(
        Roadmap.student_id == student.id
    ).all()

    return [
        {
            "id": roadmap.id,
            "student_id": roadmap.student_id,
            "title": roadmap.title,
            "description": roadmap.description,
            "current_grade": roadmap.current_grade,
            "target_grade": roadmap.target_grade,
            "status": roadmap.status,
            "created_at": roadmap.created_at,
        }
        for roadmap in roadmaps
    ]


@router.post("/me", status_code=201)
def create_roadmap(
    payload: RoadmapCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    roadmap = Roadmap(
        student_id=student.id,
        title=payload.title,
        description=payload.description,
        current_grade=payload.current_grade,
        target_grade=payload.target_grade
    )

    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    return {
        "id": roadmap.id,
        "student_id": roadmap.student_id,
        "title": roadmap.title,
        "description": roadmap.description,
        "current_grade": roadmap.current_grade,
        "target_grade": roadmap.target_grade,
        "status": roadmap.status,
        "created_at": roadmap.created_at,
    }


@router.patch("/{roadmap_id}")
def update_roadmap(
    roadmap_id: int,
    payload: RoadmapUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    roadmap = db.query(Roadmap).filter(
        Roadmap.id == roadmap_id,
        Roadmap.student_id == student.id
    ).first()

    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(roadmap, key, value)

    db.commit()
    db.refresh(roadmap)

    return {
        "id": roadmap.id,
        "student_id": roadmap.student_id,
        "title": roadmap.title,
        "description": roadmap.description,
        "current_grade": roadmap.current_grade,
        "target_grade": roadmap.target_grade,
        "status": roadmap.status,
        "created_at": roadmap.created_at,
    }


@router.delete("/{roadmap_id}")
def delete_roadmap(
    roadmap_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    roadmap = db.query(Roadmap).filter(
        Roadmap.id == roadmap_id,
        Roadmap.student_id == student.id
    ).first()

    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    db.delete(roadmap)
    db.commit()

    return {"success": True, "message": "Roadmap deleted successfully"}
