from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.roadmap import Roadmap
from app.models.milestone import Milestone

router = APIRouter(
    prefix="/api/v1/milestones",
    tags=["Milestones"]
)

class MilestoneCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    grade: int | None = Field(default=None, ge=1, le=12)
    due_date: datetime | None = None

class MilestoneUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    grade: int | None = Field(default=None, ge=1, le=12)
    status: str | None = Field(default=None, max_length=50)
    due_date: datetime | None = None

def _get_student(user, db: Session) -> Student:
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


@router.get("/roadmap/{roadmap_id}")
def get_roadmap_milestones(
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

    milestones = db.query(Milestone).filter(Milestone.roadmap_id == roadmap.id).all()

    return [
        {
            "id": milestone.id,
            "roadmap_id": milestone.roadmap_id,
            "title": milestone.title,
            "description": milestone.description,
            "grade": milestone.grade,
            "status": milestone.status,
            "due_date": milestone.due_date,
            "created_at": milestone.created_at,
        }
        for milestone in milestones
    ]


@router.post("/roadmap/{roadmap_id}", status_code=201)
def create_milestone(
    roadmap_id: int,
    payload: MilestoneCreate,
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

    milestone = Milestone(
        roadmap_id=roadmap.id,
        title=payload.title,
        description=payload.description,
        grade=payload.grade,
        due_date=payload.due_date
    )

    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    return {
        "id": milestone.id,
        "roadmap_id": milestone.roadmap_id,
        "title": milestone.title,
        "description": milestone.description,
        "grade": milestone.grade,
        "status": milestone.status,
        "due_date": milestone.due_date,
        "created_at": milestone.created_at,
    }


@router.patch("/{milestone_id}")
def update_milestone(
    milestone_id: int,
    payload: MilestoneUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    milestone = (
        db.query(Milestone)
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .filter(
            Milestone.id == milestone_id,
            Roadmap.student_id == student.id
        )
        .first()
    )

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    if payload.title is not None:
        milestone.title = payload.title
    if payload.description is not None:
        milestone.description = payload.description
    if payload.grade is not None:
        milestone.grade = payload.grade
    if payload.status is not None:
        milestone.status = payload.status
    if payload.due_date is not None:
        milestone.due_date = payload.due_date

    db.commit()
    db.refresh(milestone)

    return {
        "id": milestone.id,
        "roadmap_id": milestone.roadmap_id,
        "title": milestone.title,
        "description": milestone.description,
        "grade": milestone.grade,
        "status": milestone.status,
        "due_date": milestone.due_date,
        "created_at": milestone.created_at,
    }


@router.delete("/{milestone_id}")
def delete_milestone(
    milestone_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    milestone = (
        db.query(Milestone)
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .filter(
            Milestone.id == milestone_id,
            Roadmap.student_id == student.id
        )
        .first()
    )

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    db.delete(milestone)
    db.commit()

    return {"success": True, "message": "Milestone deleted successfully"}
