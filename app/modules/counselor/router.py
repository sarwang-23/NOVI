from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_role, get_current_organization
from app.models.counselor_assignment import CounselorStudentAssignment, CounselorProfile
from app.models.student import Student
from app.models.counselor_note import CounselorNote

router = APIRouter(
    prefix="/api/v1/counselor",
    tags=["Counselor"]
)

@router.get("/me")
def get_counselor_profile(
    counselor = Depends(require_role(["counselor", "admin", "super_admin"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not organization:
        raise HTTPException(status_code=404, detail="No organization associated")
        
    profile = db.query(CounselorProfile).filter(
        CounselorProfile.user_id == counselor.id,
        CounselorProfile.organization_id == organization.id
    ).first()
    
    return profile or {"message": "No profile exists yet"}

@router.get("/students")
def get_assigned_students(
    counselor = Depends(require_role(["counselor"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not organization:
        raise HTTPException(status_code=404, detail="No organization associated")
        
    assignments = db.query(CounselorStudentAssignment).filter(
        CounselorStudentAssignment.counselor_id == counselor.id,
        CounselorStudentAssignment.organization_id == organization.id,
        CounselorStudentAssignment.status == "active"
    ).all()
    
    student_ids = [a.student_id for a in assignments]
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    
    return {"items": students}

@router.get("/students/{student_id}/notes")
def get_student_notes(
    student_id: int,
    counselor = Depends(require_role(["counselor"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    # Verify assignment
    assignment = db.query(CounselorStudentAssignment).filter(
        CounselorStudentAssignment.counselor_id == counselor.id,
        CounselorStudentAssignment.student_id == student_id,
        CounselorStudentAssignment.status == "active"
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=403, detail="Student is not assigned to you")
        
    notes = db.query(CounselorNote).filter(
        CounselorNote.student_id == student_id,
        CounselorNote.counselor_id == counselor.id
    ).order_by(CounselorNote.created_at.desc()).all()
    
    return {"items": notes}

@router.post("/students/{student_id}/notes")
def add_student_note(
    student_id: int,
    payload: dict,
    counselor = Depends(require_role(["counselor"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    # Verify assignment
    assignment = db.query(CounselorStudentAssignment).filter(
        CounselorStudentAssignment.counselor_id == counselor.id,
        CounselorStudentAssignment.student_id == student_id,
        CounselorStudentAssignment.status == "active"
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=403, detail="Student is not assigned to you")
        
    note = CounselorNote(
        counselor_id=counselor.id,
        student_id=student_id,
        organization_id=organization.id,
        note=payload.get("note"),
        visibility=payload.get("visibility", "counselor_private")
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
