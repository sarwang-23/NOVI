from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.models.student import Student
from app.models.goal import Goal
from app.models.counselor_assignment import CounselorStudentAssignment

router = APIRouter(
    prefix="/api/v1/organization/dashboard",
    tags=["Institution Dashboard"]
)

@router.get("")
def get_dashboard_overview(
    admin = Depends(require_permission("organizations.read")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    # Aggregated metrics for the institution
    total_students = db.query(func.count(Student.id)).filter(Student.organization_id == organization.id).scalar() or 0
    
    # E.g. get goal counts for this org by joining students. For MVP, we'll return mock aggregate structure.
    # In a real app we'd do: db.query(Goal).join(Student).filter(Student.organization_id == org.id)
    
    counselor_assignments = db.query(func.count(CounselorStudentAssignment.id)).filter(
        CounselorStudentAssignment.organization_id == organization.id,
        CounselorStudentAssignment.status == "active"
    ).scalar() or 0
    
    return {
        "organization_id": organization.id,
        "metrics": {
            "total_students": total_students,
            "active_students": int(total_students * 0.8), # Mock calculation for MVP
            "total_counselor_assignments": counselor_assignments,
            "goals_completion_rate": 0.65
        },
        "recent_activity": []
    }
