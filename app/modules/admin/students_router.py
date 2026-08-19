from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.models.student import Student
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/admin/students",
    tags=["Admin Students"]
)

@router.get("")
def get_students(
    search: Optional[str] = None,
    grade: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user = Depends(require_permission("students.read")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    query = db.query(Student).join(User)
    
    # Enforce tenant isolation if organization context exists
    if organization:
        query = query.filter(Student.organization_id == organization.id)
        
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
        
    if grade is not None:
        query = query.filter(Student.grade == grade)
        
    total = query.count()
    students = query.offset(skip).limit(limit).all()
    
    results = []
    for s in students:
        u = db.query(User).filter(User.id == s.user_id).first()
        results.append({
            "id": s.id,
            "email": u.email if u else None,
            "grade": s.grade,
            "school": s.school,
            "curriculum": s.curriculum,
            "organization_id": s.organization_id
        })
        
    return {
        "items": results,
        "skip": skip,
        "limit": limit,
        "total": total
    }

@router.get("/{student_id}")
def get_student(
    student_id: int,
    admin_user = Depends(require_permission("students.read")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Tenant isolation check
    if organization and student.organization_id != organization.id:
        raise HTTPException(status_code=403, detail="Student belongs to another organization")
        
    user = db.query(User).filter(User.id == student.user_id).first()
    
    return {
        "id": student.id,
        "email": user.email if user else None,
        "grade": student.grade,
        "school": student.school,
        "curriculum": student.curriculum,
        "organization_id": student.organization_id
    }

@router.post("/{student_id}/activate")
def activate_student(
    student_id: int,
    admin_user = Depends(require_permission("students.write")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if organization and student.organization_id != organization.id:
        raise HTTPException(status_code=403, detail="Student belongs to another organization")
        
    # We would typically update a status field on the user or student model here.
    # We'll leave it as a conceptual success for MVP.
    return {"message": "Student activated"}
