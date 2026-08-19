from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.models.organization_report import OrganizationReportJob

router = APIRouter(
    prefix="/api/v1/organization/reports",
    tags=["Reports"]
)

def process_report_job(job_id: int):
    # MVP Background task
    print(f"Generating report for job {job_id}")

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
