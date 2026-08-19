from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.models.student_import import StudentImportJob
from app.services.import_processor import process_import_job
import csv
import io

router = APIRouter(
    prefix="/api/v1/organization/students/import",
    tags=["Student Import"]
)

@router.post("")
async def upload_students_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    admin=Depends(require_permission("students.import")),
    organization=Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    contents = await file.read()
    decoded = contents.decode('utf-8')
    reader = csv.reader(io.StringIO(decoded))
    rows = list(reader)

    if len(rows) < 2:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no data rows")

    # Validate header row
    header = [col.strip().lower() for col in rows[0]]
    required_cols = {"email"}
    missing = required_cols - set(header)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing)}"
        )

    total_rows = len(rows) - 1  # Subtract header

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

    background_tasks.add_task(process_import_job, job.id)

    return {
        "job_id": job.id,
        "message": "Upload successful, processing started",
        "total_rows_detected": total_rows,
    }


@router.get("/{job_id}")
def get_import_job(
    job_id: int,
    admin=Depends(require_permission("students.import")),
    organization=Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    job = db.query(StudentImportJob).filter(
        StudentImportJob.id == job_id,
        StudentImportJob.organization_id == organization.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "filename": job.filename,
        "status": job.status,
        "total_rows": job.total_rows,
        "valid_rows": job.valid_rows,
        "invalid_rows": job.invalid_rows,
        "imported_rows": job.imported_rows,
        "failed_rows": job.failed_rows,
        "error_count": job.error_count,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }
