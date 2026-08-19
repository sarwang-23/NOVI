from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.goal import Goal

router = APIRouter(
    prefix="/api/v1/goals",
    tags=["Goals"]
)


class GoalCreate(BaseModel):
    goal_type: str = Field(..., pattern="^(career|university|academic|personal)$")
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    target: str | None = Field(default=None, max_length=255)

class GoalUpdate(BaseModel):
    goal_type: str | None = Field(default=None, pattern="^(career|university|academic|personal)$")
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    target: str | None = Field(default=None, max_length=255)


def _get_student(user, db: Session) -> Student:
    """Resolve Auth0 user → DB user → student, raising 404 at each step."""
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return student


@router.get("/me", response_model=List[dict])
def get_my_goals(
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    goals = db.query(Goal).filter(Goal.student_id == student.id).all()

    return [
        {
            "id": g.id,
            "student_id": g.student_id,
            "goal_type": g.goal_type,
            "title": g.title,
            "description": g.description,
            "target": g.target,
            "status": g.status,
            "created_at": g.created_at,
        }
        for g in goals
    ]


@router.post("/me", status_code=201)
def create_goal(
    payload: GoalCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    goal = Goal(
        student_id=student.id,
        goal_type=payload.goal_type,
        title=payload.title,
        description=payload.description,
        target=payload.target
    )

    db.add(goal)
    db.commit()
    db.refresh(goal)

    return {
        "id": goal.id,
        "student_id": goal.student_id,
        "goal_type": goal.goal_type,
        "title": goal.title,
        "description": goal.description,
        "target": goal.target,
        "status": goal.status,
        "created_at": goal.created_at,
    }


@router.patch("/me/{goal_id}")
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.student_id == student.id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Goal not found"
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)

    db.commit()
    db.refresh(goal)

    return {
        "id": goal.id,
        "student_id": goal.student_id,
        "goal_type": goal.goal_type,
        "title": goal.title,
        "description": goal.description,
        "target": goal.target,
        "status": goal.status,
        "created_at": goal.created_at,
    }


@router.delete("/me/{goal_id}")
def delete_goal(
    goal_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.student_id == student.id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Goal not found"
        )

    db.delete(goal)
    db.commit()

    return {
        "success": True,
        "message": "Goal deleted successfully"
    }
