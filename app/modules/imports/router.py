from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.models.student_import import StudentImportJob
import csv
import io

router = APIRouter(
    prefix="/api/v1/organization/students/import",
    tags=["Student Import"]
)

def process_import_job(job_id: int):
    # MVP Background task to simulate processing rows
    # Real implementation would read from Cloud Storage/S3 using the job's filename
    print(f"Processing background import job {job_id}")

@router.post("")
async def upload_students_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    admin = Depends(require_permission("students.import")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
    contents = await file.read()
    decoded = contents.decode('utf-8')
    reader = csv.reader(io.StringIO(decoded))
    rows = list(reader)
    
    total_rows = len(rows) - 1 if len(rows) > 0 else 0 # Subtract header
    
    job = StudentImportJob(
        organization_id=organization.id,
        created_by=admin.id,
        filename=file.filename,
        total_rows=total_rows,
        status="validating"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # In a real system, we'd save the file to GCS/S3 here
    
    background_tasks.add_task(process_import_job, job.id)
    
    return {"job_id": job.id, "message": "Upload successful, validation started", "total_rows_detected": total_rows}

@router.get("/{job_id}")
def get_import_job(
    job_id: int,
    admin = Depends(require_permission("students.import")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    job = db.query(StudentImportJob).filter(
        StudentImportJob.id == job_id,
        StudentImportJob.organization_id == organization.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return job
