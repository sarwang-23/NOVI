from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_role
from app.models.organization_onboarding import OrganizationOnboarding
from app.models.organization import Organization
from datetime import datetime

router = APIRouter(
    prefix="/api/v1/onboarding/organization",
    tags=["Onboarding"]
)

@router.get("")
def get_onboarding_status(
    admin_user = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    # For MVP, listing all onboardings.
    # In production, organization admins might only see their own.
    onboardings = db.query(OrganizationOnboarding).all()
    return {"items": onboardings}

@router.post("")
def start_onboarding(
    payload: dict,
    admin_user = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    # Step 1: Create Organization in draft
    slug = payload.get("slug")
    if db.query(Organization).filter(Organization.slug == slug).first():
        raise HTTPException(status_code=400, detail="Organization slug already exists")
        
    org = Organization(
        name=payload.get("name"),
        slug=slug,
        organization_type=payload.get("type", "school"),
        status="draft"
    )
    db.add(org)
    db.flush()
    
    # Step 2: Create Onboarding Tracker
    onboarding = OrganizationOnboarding(
        organization_id=org.id,
        initiated_by=admin_user.id,
        status="in_progress",
        current_step="organization_information",
        completed_steps=[]
    )
    db.add(onboarding)
    db.commit()
    db.refresh(onboarding)
    
    return onboarding

@router.post("/{onboarding_id}/complete")
def complete_onboarding(
    onboarding_id: int,
    admin_user = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    onboarding = db.query(OrganizationOnboarding).filter(OrganizationOnboarding.id == onboarding_id).first()
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")
        
    onboarding.status = "active"
    onboarding.completed_at = datetime.utcnow()
    
    org = db.query(Organization).filter(Organization.id == onboarding.organization_id).first()
    if org:
        org.status = "active"
        
    db.commit()
    
    return {"message": "Onboarding completed and organization activated"}
