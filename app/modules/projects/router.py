from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.project import Project

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"]
)

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    role: str | None = Field(default=None, max_length=255)
    skills: str | None = Field(default=None, max_length=2000)
    outcome: str | None = Field(default=None)
    evidence: str | None = Field(default=None, max_length=1000)

class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    role: str | None = Field(default=None, max_length=255)
    skills: str | None = Field(default=None, max_length=2000)
    outcome: str | None = Field(default=None)
    evidence: str | None = Field(default=None, max_length=1000)


def _get_student(user, db: Session) -> Student:
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


def _serialize_project(project: Project):
    return {
        "id": project.id,
        "student_id": project.student_id,
        "title": project.title,
        "description": project.description,
        "role": project.role,
        "skills": project.skills,
        "outcome": project.outcome,
        "evidence": project.evidence,
        "created_at": project.created_at
    }


@router.get("/me")
def get_my_projects(
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    projects = db.query(Project).filter(
        Project.student_id == student.id
    ).all()

    return [_serialize_project(p) for p in projects]


@router.post("/me", status_code=201)
def create_project(
    payload: ProjectCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    project = Project(
        student_id=student.id,
        title=payload.title,
        description=payload.description,
        role=payload.role,
        skills=payload.skills,
        outcome=payload.outcome,
        evidence=payload.evidence
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return _serialize_project(project)


@router.get("/{project_id}")
def get_project(
    project_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.student_id == student.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return _serialize_project(project)


@router.patch("/{project_id}")
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.student_id == student.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if payload.title is not None:
        project.title = payload.title

    if payload.description is not None:
        project.description = payload.description

    if payload.role is not None:
        project.role = payload.role

    if payload.skills is not None:
        project.skills = payload.skills

    if payload.outcome is not None:
        project.outcome = payload.outcome

    if payload.evidence is not None:
        project.evidence = payload.evidence

    db.commit()
    db.refresh(project)

    return _serialize_project(project)
