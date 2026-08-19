from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.models.counselor_assignment import CounselorStudentAssignment
from app.models.student import Student
from datetime import datetime

router = APIRouter(
    prefix="/api/v1/organization/counselors",
    tags=["Counselor Assignments"]
)

@router.post("/{counselor_id}/students/{student_id}")
def assign_student_to_counselor(
    counselor_id: int,
    student_id: int,
    admin = Depends(require_permission("students.assign")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not organization:
        raise HTTPException(status_code=404, detail="No organization associated")
        
    # Verify student belongs to this organization
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.organization_id == organization.id
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found in this organization")
        
    assignment = db.query(CounselorStudentAssignment).filter(
        CounselorStudentAssignment.counselor_id == counselor_id,
        CounselorStudentAssignment.student_id == student_id
    ).first()
    
    if assignment:
        assignment.status = "active"
        assignment.unassigned_at = None
    else:
        assignment = CounselorStudentAssignment(
            counselor_id=counselor_id,
            student_id=student_id,
            organization_id=organization.id,
            assigned_by=admin.id
        )
        db.add(assignment)
        
    db.commit()
    db.refresh(assignment)
    return assignment

@router.delete("/{counselor_id}/students/{student_id}")
def unassign_student(
    counselor_id: int,
    student_id: int,
    admin = Depends(require_permission("students.assign")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    assignment = db.query(CounselorStudentAssignment).filter(
        CounselorStudentAssignment.counselor_id == counselor_id,
        CounselorStudentAssignment.student_id == student_id,
        CounselorStudentAssignment.organization_id == organization.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    assignment.status = "inactive"
    assignment.unassigned_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Student unassigned"}
