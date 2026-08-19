from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.models.organization_report import OrganizationReportJob

router = APIRouter(
    prefix="/api/v1/organization/reports",
    tags=["Reports"]
)

from app.database.connection import SessionLocal
from app.models.student import Student
from app.models.goal import Goal
import json

def process_report_job(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(OrganizationReportJob).filter(OrganizationReportJob.id == job_id).first()
        if not job:
            return
            
        job.status = "processing"
        db.commit()
        
        # Simple Deterministic Aggregation
        student_count = db.query(Student).filter(Student.organization_id == job.organization_id).count()
        
        # Get students in org
        org_students = db.query(Student).filter(Student.organization_id == job.organization_id).all()
        student_ids = [s.id for s in org_students]
        
        active_goals = db.query(Goal).filter(Goal.student_id.in_(student_ids), Goal.status == "in_progress").count()
        completed_goals = db.query(Goal).filter(Goal.student_id.in_(student_ids), Goal.status == "completed").count()
        
        report_data = {
            "total_students": student_count,
            "active_goals": active_goals,
            "completed_goals": completed_goals
        }
        
        job.file_reference = json.dumps(report_data) # In reality, save to S3 and store URL
        job.status = "completed"
        db.commit()
    except Exception as e:
        db.rollback()
        job = db.query(OrganizationReportJob).filter(OrganizationReportJob.id == job_id).first()
        if job:
            job.status = "failed"
            db.commit()
    finally:
        db.close()

@router.post("")
def generate_report(
    payload: dict,
    background_tasks: BackgroundTasks,
    admin = Depends(require_permission("reports.generate")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    job = OrganizationReportJob(
        organization_id=organization.id,
        requested_by=admin.id,
        report_type=payload.get("report_type", "student_engagement"),
        parameters=payload.get("parameters", {})
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    background_tasks.add_task(process_report_job, job.id)
    
    return {"job_id": job.id, "message": "Report generation started"}

@router.get("/{job_id}")
def get_report_status(
    job_id: int,
    admin = Depends(require_permission("reports.generate")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    job = db.query(OrganizationReportJob).filter(
        OrganizationReportJob.id == job_id,
        OrganizationReportJob.organization_id == organization.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Report job not found")
        
    return job
