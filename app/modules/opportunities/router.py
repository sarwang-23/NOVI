from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.opportunity import Opportunity, StudentOpportunity

router = APIRouter(
    prefix="/api/v1/opportunities",
    tags=["Opportunities"]
)

# --- SCHEMAS ---

class OpportunityOut(BaseModel):
    id: int
    title: str
    opportunity_type: str
    provider: Optional[str]
    deadline: Optional[date]
    location: Optional[str]
    status: str

    class Config:
        from_attributes = True

class OpportunityDetailOut(OpportunityOut):
    description: Optional[str]
    url: Optional[str]
    eligibility: Optional[List[str]]
    skills: Optional[List[str]]
    interests: Optional[List[str]]

class StudentOpportunityOut(BaseModel):
    id: int
    student_id: int
    opportunity_id: int
    status: str
    opportunity: Optional[OpportunityOut] = None

    class Config:
        from_attributes = True

class StudentOpportunityStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(viewed|saved|dismissed|applied|completed)$")

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

@router.get("", response_model=dict)
def get_opportunities(
    search: Optional[str] = None,
    opportunity_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity).filter(Opportunity.status == "active")

    if search:
        query = query.filter(
            or_(
                Opportunity.title.ilike(f"%{search}%"),
                Opportunity.provider.ilike(f"%{search}%")
            )
        )
    if opportunity_type:
        query = query.filter(Opportunity.opportunity_type == opportunity_type)

    total = query.count()
    opportunities = query.order_by(Opportunity.deadline.asc().nullslast()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [OpportunityOut.model_validate(o).model_dump() for o in opportunities]
    }

@router.get("/me", response_model=List[StudentOpportunityOut])
def get_my_opportunities(
    status: Optional[str] = None,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    query = db.query(StudentOpportunity).filter(StudentOpportunity.student_id == student.id)
    if status:
        query = query.filter(StudentOpportunity.status == status)
        
    student_opps = query.all()
    
    result = []
    for so in student_opps:
        opp = db.query(Opportunity).filter(Opportunity.id == so.opportunity_id).first()
        result.append({
            "id": so.id,
            "student_id": so.student_id,
            "opportunity_id": so.opportunity_id,
            "status": so.status,
            "opportunity": {
                "id": opp.id,
                "title": opp.title,
                "opportunity_type": opp.opportunity_type,
                "provider": opp.provider,
                "deadline": opp.deadline,
                "location": opp.location,
                "status": opp.status
            } if opp else None
        })
        
    return result

@router.get("/{opportunity_id}", response_model=OpportunityDetailOut)
def get_opportunity_by_id(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id, Opportunity.status == "active").first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    return opportunity

@router.post("/{opportunity_id}/status", response_model=StudentOpportunityOut)
def set_opportunity_status(
    opportunity_id: int,
    payload: StudentOpportunityStatusUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    # Verify opportunity exists
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    student_opp = db.query(StudentOpportunity).filter(
        StudentOpportunity.student_id == student.id,
        StudentOpportunity.opportunity_id == opportunity_id
    ).first()
    
    if student_opp:
        student_opp.status = payload.status
    else:
        student_opp = StudentOpportunity(
            student_id=student.id,
            opportunity_id=opportunity_id,
            status=payload.status
        )
        db.add(student_opp)
        
    db.commit()
    db.refresh(student_opp)
    
    return {
        "id": student_opp.id,
        "student_id": student_opp.student_id,
        "opportunity_id": student_opp.opportunity_id,
        "status": student_opp.status,
        "opportunity": {
            "id": opportunity.id,
            "title": opportunity.title,
            "opportunity_type": opportunity.opportunity_type,
            "provider": opportunity.provider,
            "deadline": opportunity.deadline,
            "location": opportunity.location,
            "status": opportunity.status
        }
    }
