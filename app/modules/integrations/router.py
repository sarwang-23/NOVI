import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.core.config import settings
from app.models.integration import OrganizationIntegration, IntegrationSyncJob
from app.services.integration import GenericIntegrationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Enterprise Integrations"]
)


# --- SCHEMAS ---

class IntegrationConfig(BaseModel):
    integration_type: str
    provider: str
    configuration: dict


class WebhookPayload(BaseModel):
    event_type: Optional[str] = None
    data: Optional[dict] = None
    timestamp: Optional[str] = None
    signature: Optional[str] = None


# --- WEBHOOK PROCESSING ---

def _verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook HMAC signature."""
    if not secret or not signature:
        return False
    expected = hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _process_webhook_background(provider: str, payload: dict, integration_id: Optional[int], db_url: str):
    """Background task to process incoming webhook data."""
    from app.database.connection import SessionLocal

    db = SessionLocal()
    try:
        event_type = payload.get("event_type", "unknown")
        data = payload.get("data", {})

        logger.info(f"[Webhook] Processing {provider} event: {event_type}")

        # Route webhook events to appropriate handlers
        if provider == "clever":
            _handle_clever_webhook(event_type, data, db)
        elif provider == "powerschool":
            _handle_powerschool_webhook(event_type, data, db)
        elif provider == "canvas":
            _handle_canvas_webhook(event_type, data, db)
        else:
            logger.warning(f"[Webhook] No handler for provider: {provider}")

        # Update integration last_sync_at if linked
        if integration_id:
            integration = db.query(OrganizationIntegration).filter(
                OrganizationIntegration.id == integration_id
            ).first()
            if integration:
                integration.last_sync_at = datetime.utcnow()
                db.commit()

        logger.info(f"[Webhook] {provider} event {event_type} processed successfully")

    except Exception as exc:
        logger.error(f"[Webhook] Processing failed for {provider}: {exc}")
    finally:
        db.close()


def _handle_clever_webhook(event_type: str, data: dict, db: Session):
    """Handle Clever webhook events."""
    if event_type in ("student.created", "student.updated"):
        external_id = data.get("id")
        logger.info(f"[Clever] Student sync: {external_id}")
        # In production: upsert student from Clever data
    elif event_type == "student.deleted":
        external_id = data.get("id")
        logger.info(f"[Clever] Student deleted: {external_id}")
        # In production: soft-delete or unlink student
    else:
        logger.info(f"[Clever] Unhandled event: {event_type}")


def _handle_powerschool_webhook(event_type: str, data: dict, db: Session):
    """Handle PowerSchool webhook events."""
    if event_type == "student.changed":
        logger.info(f"[PowerSchool] Student changed: {data.get('id')}")
        # In production: upsert student from PowerSchool data
    else:
        logger.info(f"[PowerSchool] Unhandled event: {event_type}")


def _handle_canvas_webhook(event_type: str, data: dict, db: Session):
    """Handle Canvas webhook events."""
    if event_type == "enrollment.created":
        logger.info(f"[Canvas] New enrollment: {data}")
        # In production: sync enrollment data
    elif event_type == "submission.created":
        logger.info(f"[Canvas] New submission: {data}")
        # In production: sync submission data
    else:
        logger.info(f"[Canvas] Unhandled event: {event_type}")


# --- ENDPOINTS ---

@router.post("/organization/integrations")
def configure_integration(
    payload: IntegrationConfig,
    admin=Depends(__import__("app.core.rbac", fromlist=["require_role"]).require_role(["super_admin", "organization_admin"])),
    organization=Depends(__import__("app.core.rbac", fromlist=["get_current_organization"]).get_current_organization),
    db: Session = Depends(get_db),
):
    if not organization:
        raise HTTPException(status_code=404, detail="No organization associated")

    integration = OrganizationIntegration(
        organization_id=organization.id,
        integration_type=payload.integration_type,
        provider=payload.provider,
        status="pending",
        configuration=payload.configuration,
    )

    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


@router.post("/organization/integrations/{integration_id}/sync")
def trigger_sync(
    integration_id: int,
    background_tasks: BackgroundTasks,
    admin=Depends(__import__("app.core.rbac", fromlist=["require_role"]).require_role(["super_admin", "organization_admin"])),
    organization=Depends(__import__("app.core.rbac", fromlist=["get_current_organization"]).get_current_organization),
    db: Session = Depends(get_db),
):
    import uuid

    integration = db.query(OrganizationIntegration).filter(
        OrganizationIntegration.id == integration_id,
        OrganizationIntegration.organization_id == organization.id,
    ).first()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    if integration.status != "connected":
        raise HTTPException(status_code=400, detail="Integration must be connected before syncing")

    job = IntegrationSyncJob(
        organization_id=organization.id,
        integration_id=integration.id,
        idempotency_key=str(uuid.uuid4()),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(GenericIntegrationService.process_sync_job, db, job.id)

    return {"job_id": job.id, "message": "Sync queued"}


@router.post("/integrations/webhooks/{provider}")
async def handle_webhook(
    provider: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Generic webhook receiver. Validates signatures, extracts tenant context,
    and triggers idempotent background processing jobs.
    """
    body = await request.body()

    # Parse payload
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Verify signature if configured
    webhook_secret = getattr(settings, f"WEBHOOK_SECRET_{provider.upper()}", "")
    if webhook_secret:
        signature = request.headers.get("X-Webhook-Signature", "")
        if not _verify_webhook_signature(body, signature, webhook_secret):
            logger.warning(f"[Webhook] Invalid signature from {provider}")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Find linked integration
    integration_id = None
    org_slug = request.headers.get("X-Organization-Slug")
    if org_slug:
        from app.models.organization import Organization
        org = db.query(Organization).filter(Organization.slug == org_slug).first()
        if org:
            integration = db.query(OrganizationIntegration).filter(
                OrganizationIntegration.organization_id == org.id,
                OrganizationIntegration.provider == provider,
            ).first()
            if integration:
                integration_id = integration.id

    # Queue background processing
    from app.database.connection import settings as db_settings
    background_tasks.add_task(
        _process_webhook_background,
        provider=provider,
        payload=payload,
        integration_id=integration_id,
        db_url=db_settings.DATABASE_URL if hasattr(db_settings, "DATABASE_URL") else "",
    )

    return {
        "message": "Webhook received and queued for processing",
        "provider": provider,
        "event_type": payload.get("event_type"),
    }
