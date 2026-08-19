from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.roadmap import Roadmap
from app.models.roadmap_year_plan import RoadmapYearPlan
from app.models.roadmap_monthly_plan import MonthlyPlan
from app.models.roadmap_weekly_plan import WeeklyPlan

plans_router = APIRouter(
    prefix="/api/v1/roadmaps/me",
    tags=["Roadmap Plans"]
)

# --- SCHEMAS ---

class YearPlanCreate(BaseModel):
    roadmap_id: int
    academic_year: str
    grade: Optional[int] = None
    title: str
    description: Optional[str] = None
    academic_objectives: Optional[list] = None
    career_objectives: Optional[list] = None
    university_objectives: Optional[list] = None
    personal_objectives: Optional[list] = None

class YearPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    academic_objectives: Optional[list] = None
    career_objectives: Optional[list] = None
    university_objectives: Optional[list] = None
    personal_objectives: Optional[list] = None

class MonthlyPlanCreate(BaseModel):
    year_plan_id: int
    year: int
    month: int = Field(..., ge=1, le=12)
    title: str
    description: Optional[str] = None
    objectives: Optional[list] = None
    priority: Optional[str] = "medium"

class MonthlyPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    objectives: Optional[list] = None
    priority: Optional[str] = None

class WeeklyPlanCreate(BaseModel):
    monthly_plan_id: int
    week_start: date
    week_end: date
    title: str
    objectives: Optional[list] = None
    priority: Optional[str] = "medium"

class WeeklyPlanUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    objectives: Optional[list] = None
    priority: Optional[str] = None


# --- HELPER ---

def _get_student(user, db: Session) -> Student:
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student

# --- YEAR PLANS ---

@plans_router.get("/year-plans")
def get_year_plans(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plans = db.query(RoadmapYearPlan).filter(RoadmapYearPlan.student_id == student.id).all()
    return plans

@plans_router.post("/year-plans")
def create_year_plan(payload: YearPlanCreate, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    
    # Verify roadmap belongs to student
    roadmap = db.query(Roadmap).filter(Roadmap.id == payload.roadmap_id, Roadmap.student_id == student.id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found or access denied")
        
    plan = RoadmapYearPlan(
        student_id=student.id,
        roadmap_id=roadmap.id,
        academic_year=payload.academic_year,
        grade=payload.grade,
        title=payload.title,
        description=payload.description,
        academic_objectives=payload.academic_objectives,
        career_objectives=payload.career_objectives,
        university_objectives=payload.university_objectives,
        personal_objectives=payload.personal_objectives
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@plans_router.get("/year-plans/{plan_id}")
def get_year_plan(plan_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plan = db.query(RoadmapYearPlan).filter(RoadmapYearPlan.id == plan_id, RoadmapYearPlan.student_id == student.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Year plan not found")
    return plan

@plans_router.put("/year-plans/{plan_id}")
def update_year_plan(plan_id: int, payload: YearPlanUpdate, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plan = db.query(RoadmapYearPlan).filter(RoadmapYearPlan.id == plan_id, RoadmapYearPlan.student_id == student.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Year plan not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan

@plans_router.delete("/year-plans/{plan_id}")
def delete_year_plan(plan_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plan = db.query(RoadmapYearPlan).filter(RoadmapYearPlan.id == plan_id, RoadmapYearPlan.student_id == student.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Year plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Year plan deleted"}


# --- MONTHLY PLANS ---

@plans_router.get("/monthly-plans")
def get_monthly_plans(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plans = db.query(MonthlyPlan).filter(MonthlyPlan.student_id == student.id).all()
    return plans

@plans_router.post("/monthly-plans")
def create_monthly_plan(payload: MonthlyPlanCreate, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    
    # Verify year plan belongs to student
    year_plan = db.query(RoadmapYearPlan).filter(RoadmapYearPlan.id == payload.year_plan_id, RoadmapYearPlan.student_id == student.id).first()
    if not year_plan:
        raise HTTPException(status_code=404, detail="Year plan not found or access denied")
        
    plan = MonthlyPlan(
        student_id=student.id,
        year_plan_id=year_plan.id,
        year=payload.year,
        month=payload.month,
        title=payload.title,
        description=payload.description,
        objectives=payload.objectives,
        priority=payload.priority
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@plans_router.get("/monthly-plans/current")
def get_current_monthly_plan(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    now = date.today()
    plan = db.query(MonthlyPlan).filter(
        MonthlyPlan.student_id == student.id,
        MonthlyPlan.year == now.year,
        MonthlyPlan.month == now.month
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Current monthly plan not found")
    return plan

@plans_router.get("/monthly-plans/{plan_id}")
def get_monthly_plan(plan_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id, MonthlyPlan.student_id == student.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    return plan

@plans_router.put("/monthly-plans/{plan_id}")
def update_monthly_plan(plan_id: int, payload: MonthlyPlanUpdate, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id, MonthlyPlan.student_id == student.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan

@plans_router.delete("/monthly-plans/{plan_id}")
def delete_monthly_plan(plan_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id, MonthlyPlan.student_id == student.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Monthly plan deleted"}


# --- WEEKLY PLANS ---

@plans_router.get("/weekly-plans")
def get_weekly_plans(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plans = db.query(WeeklyPlan).filter(WeeklyPlan.student_id == student.id).all()
    return plans

@plans_router.post("/weekly-plans")
def create_weekly_plan(payload: WeeklyPlanCreate, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    
    if payload.week_start > payload.week_end:
        raise HTTPException(status_code=400, detail="Week start must be before week end")
        
    # Verify monthly plan belongs to student
    monthly_plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == payload.monthly_plan_id, MonthlyPlan.student_id == student.id).first()
    if not monthly_plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found or access denied")
        
    # Prevent duplicate
    existing = db.query(WeeklyPlan).filter(
        WeeklyPlan.student_id == student.id,
        WeeklyPlan.week_start == payload.week_start
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Weekly plan for this start date already exists")
        
    plan = WeeklyPlan(
        student_id=student.id,
        monthly_plan_id=monthly_plan.id,
        week_start=payload.week_start,
        week_end=payload.week_end,
        title=payload.title,
        objectives=payload.objectives,
        priority=payload.priority
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@plans_router.get("/weekly-plans/current")
def get_current_weekly_plan(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    now = date.today()
    plan = db.query(WeeklyPlan).filter(
        WeeklyPlan.student_id == student.id,
        WeeklyPlan.week_start <= now,
        WeeklyPlan.week_end >= now
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Current weekly plan not found")
    return plan

@plans_router.get("/weekly-plans/{plan_id}")
def get_weekly_plan(plan_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plan = db.query(WeeklyPlan).filter(WeeklyPlan.id == plan_id, WeeklyPlan.student_id == student.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Weekly plan not found")
    return plan

@plans_router.put("/weekly-plans/{plan_id}")
def update_weekly_plan(plan_id: int, payload: WeeklyPlanUpdate, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plan = db.query(WeeklyPlan).filter(WeeklyPlan.id == plan_id, WeeklyPlan.student_id == student.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Weekly plan not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan

@plans_router.delete("/weekly-plans/{plan_id}")
def delete_weekly_plan(plan_id: int, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    plan = db.query(WeeklyPlan).filter(WeeklyPlan.id == plan_id, WeeklyPlan.student_id == student.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Weekly plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Weekly plan deleted"}
