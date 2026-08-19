from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import secrets
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.parent import Parent, ParentStudent, ParentStudentInvitation
from app.models.student import Student
from app.services.parent_dashboard import ParentDashboardService

router = APIRouter(
    prefix="/api/v1/parent",
    tags=["Parent"]
)

# --- SCHEMAS ---

class InviteStudentRequest(BaseModel):
    student_email: str
    relationship_type: Optional[str] = "parent"

class AcceptInviteRequest(BaseModel):
    token: str

# --- HELPER ---

def _get_parent_user(user, db: Session) -> User:
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def _get_parent(db_user: User, db: Session) -> Parent:
    parent = db.query(Parent).filter(Parent.user_id == db_user.id).first()
    if not parent:
        # Auto-provision parent profile if it doesn't exist
        parent = Parent(user_id=db_user.id)
        db.add(parent)
        db.commit()
        db.refresh(parent)
    return parent

# --- ENDPOINTS ---

@router.get("/me")
def get_parent_me(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    db_user = _get_parent_user(user, db)
    parent = _get_parent(db_user, db)
    return {
        "id": parent.id,
        "user_id": parent.user_id,
        "relationship_status": parent.relationship_status,
        "created_at": parent.created_at
    }

@router.get("/students")
def get_parent_students(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    db_user = _get_parent_user(user, db)
    parent = _get_parent(db_user, db)
    
    relationships = db.query(ParentStudent).filter(ParentStudent.parent_id == parent.id).all()
    results = []
    
    for rel in relationships:
        student = db.query(Student).filter(Student.id == rel.student_id).first()
        if student:
            s_user = db.query(User).filter(User.id == student.user_id).first()
            results.append({
                "relationship_id": rel.id,
                "student_id": student.id,
                "student_email": s_user.email if s_user else None,
                "relationship_type": rel.relationship_type,
                "status": rel.status
            })
            
    return {"items": results}

@router.post("/students/invite")
def invite_student(payload: InviteStudentRequest, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    db_user = _get_parent_user(user, db)
    parent = _get_parent(db_user, db)
    
    # Find student user by email
    student_user = db.query(User).filter(User.email == payload.student_email).first()
    if not student_user:
        raise HTTPException(status_code=404, detail="Student not found with this email")
        
    student = db.query(Student).filter(Student.user_id == student_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="User is not a student")
        
    # Check if already invited or linked
    existing = db.query(ParentStudent).filter(
        ParentStudent.parent_id == parent.id,
        ParentStudent.student_id == student.id
    ).first()
    
    if existing and existing.status == "active":
        raise HTTPException(status_code=409, detail="Already linked to this student")
        
    token = secrets.token_urlsafe(32)
    invitation = ParentStudentInvitation(
        parent_id=parent.id,
        student_id=student.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    db.add(invitation)
    db.commit()
    
    # In reality, this would send an email/notification to the student.
    return {"message": "Invitation sent successfully", "token": token} # Token returned for MVP testing only

@router.get("/dashboard")
def get_parent_dashboard(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    db_user = _get_parent_user(user, db)
    return ParentDashboardService.get_dashboard(db_user, db)

# Note: Student-side accept endpoint should ideally be in student_router.py 
# but placed here for modularity in this phase.
@router.post("/student-accept-invite")
def student_accept_invite(payload: AcceptInviteRequest, user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    db_user = _get_parent_user(user, db)
    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=403, detail="Only students can accept parent invitations")
        
    invitation = db.query(ParentStudentInvitation).filter(
        ParentStudentInvitation.token == payload.token,
        ParentStudentInvitation.student_id == student.id,
        ParentStudentInvitation.status == "pending"
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid or expired invitation")
        
    if invitation.expires_at < datetime.utcnow():
        invitation.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="Invitation has expired")
        
    # Accept invite
    invitation.status = "accepted"
    invitation.accepted_at = datetime.utcnow()
    
    # Create relationship
    rel = ParentStudent(
        parent_id=invitation.parent_id,
        student_id=student.id,
        relationship_type="parent",
        status="active",
        invited_by="parent"
    )
    db.add(rel)
    db.commit()
    
    return {"message": "Invitation accepted successfully"}
