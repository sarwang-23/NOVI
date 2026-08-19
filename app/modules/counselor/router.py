from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_role, get_current_organization
from app.models.counselor_assignment import CounselorStudentAssignment, CounselorProfile
from app.models.student import Student
from app.models.counselor_note import CounselorNote
from app.models.user import User
from app.models.goal import Goal
from app.models.application import Application

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
    
    results = []
    for student in students:
        s_user = db.query(User).filter(User.id == student.user_id).first()
        active_goals = db.query(Goal).filter(Goal.student_id == student.id, Goal.status == "in_progress").count()
        applications = db.query(Application).filter(Application.student_id == student.id).count()
        
        results.append({
            "student_id": student.id,
            "first_name": s_user.first_name if s_user and hasattr(s_user, "first_name") else "Student",
            "last_name": s_user.last_name if s_user and hasattr(s_user, "last_name") else "",
            "email": s_user.email if s_user else None,
            "grade": student.grade,
            "school": student.school,
            "progress_aggregation": {
                "active_goals_count": active_goals,
                "applications_count": applications
            }
        })
    
    return {"items": results}

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
