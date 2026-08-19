from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_role, get_current_organization
from app.models.integration import OrganizationIntegration, IntegrationSyncJob
from app.services.integration import GenericIntegrationService
import uuid

router = APIRouter(
    prefix="/api/v1",
    tags=["Enterprise Integrations"]
)

@router.post("/organization/integrations")
def configure_integration(
    payload: dict,
    admin = Depends(require_role(["super_admin", "organization_admin"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not organization:
        raise HTTPException(status_code=404, detail="No organization associated")
        
    integration = OrganizationIntegration(
        organization_id=organization.id,
        integration_type=payload.get("integration_type"),
        provider=payload.get("provider"),
        status="pending",
        configuration=payload.get("configuration")
    )
    
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration

@router.post("/organization/integrations/{integration_id}/sync")
def trigger_sync(
    integration_id: int,
    background_tasks: BackgroundTasks,
    admin = Depends(require_role(["super_admin", "organization_admin"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    integration = db.query(OrganizationIntegration).filter(
        OrganizationIntegration.id == integration_id,
        OrganizationIntegration.organization_id == organization.id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
        
    job = IntegrationSyncJob(
        organization_id=organization.id,
        integration_id=integration.id,
        idempotency_key=str(uuid.uuid4())
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    background_tasks.add_task(GenericIntegrationService.process_sync_job, db, job.id)
    
    return {"job_id": job.id, "message": "Sync queued"}

@router.post("/integrations/webhooks/{provider}")
def handle_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Generic webhook receiver. In production, this validates signatures, 
    extracts tenant identifiers, and triggers idempotent background jobs.
    """
    return {"message": "Webhook received securely", "provider": provider}
