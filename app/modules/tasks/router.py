from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.task import Task
from app.models.roadmap import Roadmap
from app.models.milestone import Milestone

router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["Tasks"]
)

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    roadmap_id: int | None = None
    milestone_id: int | None = None
    priority: str = Field(default="medium", min_length=1, max_length=50)
    due_date: datetime | None = None

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    priority: str | None = Field(default=None, min_length=1, max_length=50)
    due_date: datetime | None = None
    status: str | None = Field(default=None, min_length=1, max_length=50)


def _get_student(user, db: Session) -> Student:
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


def _task_response(task: Task):
    return {
        "id": task.id,
        "student_id": task.student_id,
        "roadmap_id": task.roadmap_id,
        "milestone_id": task.milestone_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date,
        "created_at": task.created_at,
        "completed_at": task.completed_at,
    }


@router.get("/me")
def get_my_tasks(
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    tasks = db.query(Task).filter(
        Task.student_id == student.id
    ).order_by(
        Task.created_at.desc()
    ).all()

    return [_task_response(task) for task in tasks]


@router.post("/me", status_code=201)
def create_task(
    payload: TaskCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    if payload.roadmap_id is not None:
        roadmap = db.query(Roadmap).filter(
            Roadmap.id == payload.roadmap_id,
            Roadmap.student_id == student.id
        ).first()

        if not roadmap:
            raise HTTPException(
                status_code=404,
                detail="Roadmap not found"
            )

    if payload.milestone_id is not None:
        milestone = db.query(Milestone).join(
            Roadmap,
            Roadmap.id == Milestone.roadmap_id
        ).filter(
            Milestone.id == payload.milestone_id,
            Roadmap.student_id == student.id
        ).first()

        if not milestone:
            raise HTTPException(
                status_code=404,
                detail="Milestone not found"
            )

    task = Task(
        student_id=student.id,
        roadmap_id=payload.roadmap_id,
        milestone_id=payload.milestone_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return _task_response(task)


@router.get("/{task_id}")
def get_task(
    task_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.student_id == student.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return _task_response(task)


@router.patch("/{task_id}")
def update_task(
    task_id: int,
    payload: TaskUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.student_id == student.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if payload.title is not None:
        task.title = payload.title

    if payload.description is not None:
        task.description = payload.description

    if payload.priority is not None:
        task.priority = payload.priority

    if payload.due_date is not None:
        task.due_date = payload.due_date

    if payload.status is not None:
        task.status = payload.status

        if payload.status == "completed":
            task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return _task_response(task)


@router.post("/{task_id}/complete")
def complete_task(
    task_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.student_id == student.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.status = "completed"
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return _task_response(task)


@router.post("/{task_id}/skip")
def skip_task(
    task_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.student_id == student.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.status = "skipped"

    db.commit()
    db.refresh(task)

    return _task_response(task)
