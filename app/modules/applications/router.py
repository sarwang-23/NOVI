from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.application import Application, ApplicationRequirement
from app.models.student_outcome import StudentOutcome

router = APIRouter(
    prefix="/api/v1/applications",
    tags=["Applications"]
)

# --- SCHEMAS ---

class ApplicationCreate(BaseModel):
    university_id: Optional[int] = None
    program_name: str
    target_term: Optional[str] = None
    application_type: Optional[str] = None
    application_deadline: Optional[date] = None

class ApplicationUpdate(BaseModel):
    program_name: Optional[str] = None
    target_term: Optional[str] = None
    application_type: Optional[str] = None
    application_deadline: Optional[date] = None
    status: Optional[str] = Field(default=None, pattern="^(draft|planning|in_progress|ready|submitted|accepted|rejected|waitlisted|enrolled)$")

class ApplicationRequirementCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None

class ApplicationRequirementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = Field(default=None, pattern="^(pending|in_progress|completed|waived)$")

class OutcomeCreate(BaseModel):
    outcome_type: str = Field(..., pattern="^(admission|scholarship|job_offer|certification)$")
    title: str
    description: Optional[str] = None
    achieved_at: Optional[date] = None
    source: Optional[str] = None

class OutcomeUpdate(BaseModel):
    outcome_type: Optional[str] = Field(default=None, pattern="^(admission|scholarship|job_offer|certification)$")
    title: Optional[str] = None
    description: Optional[str] = None
    achieved_at: Optional[date] = None
    source: Optional[str] = None

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

@router.get("/me", response_model=List[dict])
def get_my_applications(
    status: Optional[str] = None,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    query = db.query(Application).filter(Application.student_id == student.id)
    if status:
        query = query.filter(Application.status == status)
        
    applications = query.all()
    
    result = []
    for app in applications:
        result.append({
            "id": app.id,
            "university_id": app.university_id,
            "program_name": app.program_name,
            "target_term": app.target_term,
            "application_type": app.application_type,
            "application_deadline": app.application_deadline,
            "status": app.status,
            "submitted_at": app.submitted_at
        })
        
    return result

@router.post("/me", status_code=201)
def create_application(
    payload: ApplicationCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    application = Application(
        student_id=student.id,
        university_id=payload.university_id,
        program_name=payload.program_name,
        target_term=payload.target_term,
        application_type=payload.application_type,
        application_deadline=payload.application_deadline
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return {
        "id": application.id,
        "university_id": application.university_id,
        "program_name": application.program_name,
        "target_term": application.target_term,
        "application_type": application.application_type,
        "application_deadline": application.application_deadline,
        "status": application.status
    }

@router.patch("/me/{app_id}")
def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    application = db.query(Application).filter(
        Application.id == app_id,
        Application.student_id == student.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    if update_data.get("status") == "submitted" and application.status != "submitted":
        application.submitted_at = datetime.utcnow()
        
    for key, value in update_data.items():
        setattr(application, key, value)
        
    db.commit()
    db.refresh(application)
    
    return {
        "id": application.id,
        "status": application.status,
        "program_name": application.program_name
    }

@router.delete("/me/{app_id}")
def delete_application(
    app_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    application = db.query(Application).filter(
        Application.id == app_id,
        Application.student_id == student.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    db.delete(application)
    db.commit()
    
    return {"success": True, "message": "Application deleted"}

@router.get("/me/{app_id}/requirements")
def get_application_requirements(
    app_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    application = db.query(Application).filter(
        Application.id == app_id,
        Application.student_id == student.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    reqs = db.query(ApplicationRequirement).filter(ApplicationRequirement.application_id == app_id).all()
    
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "status": r.status,
            "due_date": r.due_date,
            "completed_at": r.completed_at
        } for r in reqs
    ]

@router.post("/me/{app_id}/requirements", status_code=201)
def add_application_requirement(
    app_id: int,
    payload: ApplicationRequirementCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    application = db.query(Application).filter(
        Application.id == app_id,
        Application.student_id == student.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    req = ApplicationRequirement(
        application_id=app_id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date
    )
    
    db.add(req)
    db.commit()
    db.refresh(req)
    
    return {
        "id": req.id,
        "title": req.title,
        "status": req.status,
        "due_date": req.due_date
    }

@router.patch("/me/requirements/{req_id}")
def update_application_requirement(
    req_id: int,
    payload: ApplicationRequirementUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    req = db.query(ApplicationRequirement).join(Application).filter(
        ApplicationRequirement.id == req_id,
        Application.student_id == student.id
    ).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    if update_data.get("status") == "completed" and req.status != "completed":
        req.completed_at = datetime.utcnow()
        
    for key, value in update_data.items():
        setattr(req, key, value)
        
    db.commit()
    db.refresh(req)
    
    return {
        "id": req.id,
        "status": req.status,
        "completed_at": req.completed_at
    }

@router.get("/me/timeline")
def get_application_timeline(
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    apps = db.query(Application).filter(Application.student_id == student.id).all()
    app_ids = [a.id for a in apps]
    
    reqs = db.query(ApplicationRequirement).filter(ApplicationRequirement.application_id.in_(app_ids)).all()
    
    timeline = []
    for a in apps:
        if a.application_deadline:
            timeline.append({
                "type": "application_deadline",
                "date": a.application_deadline,
                "title": f"{a.program_name} Deadline",
                "application_id": a.id,
                "status": a.status
            })
            
    for r in reqs:
        if r.due_date:
            timeline.append({
                "type": "requirement_deadline",
                "date": r.due_date,
                "title": r.title,
                "application_id": r.application_id,
                "status": r.status
            })
            
    # Sort chronologically
    timeline.sort(key=lambda x: x["date"])
    return timeline

@router.get("/me/outcomes")
def get_my_outcomes(
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    outcomes = db.query(StudentOutcome).filter(StudentOutcome.student_id == student.id).all()
    return [
        {
            "id": o.id,
            "outcome_type": o.outcome_type,
            "title": o.title,
            "description": o.description,
            "achieved_at": o.achieved_at,
            "source": o.source
        } for o in outcomes
    ]

@router.post("/me/outcomes", status_code=201)
def create_outcome(
    payload: OutcomeCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    outcome = StudentOutcome(
        student_id=student.id,
        outcome_type=payload.outcome_type,
        title=payload.title,
        description=payload.description,
        achieved_at=payload.achieved_at,
        source=payload.source
    )
    
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    
    return {
        "id": outcome.id,
        "title": outcome.title,
        "outcome_type": outcome.outcome_type
    }
