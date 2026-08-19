from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.models.organization_settings import OrganizationSettings

router = APIRouter(
    prefix="/api/v1/organizations/me/settings",
    tags=["Organizations"]
)

@router.get("")
def get_organization_settings(
    user = Depends(require_permission("settings.write")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not organization:
        raise HTTPException(status_code=404, detail="No organization associated with user")
        
    settings = db.query(OrganizationSettings).filter(OrganizationSettings.organization_id == organization.id).first()
    if not settings:
        # Return defaults if not configured
        return {
            "timezone": "UTC",
            "ai_enabled": True,
            "parent_enabled": True,
            "counselor_enabled": True
        }
        
    return settings

@router.put("")
def update_organization_settings(
    payload: dict,
    user = Depends(require_permission("settings.write")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not organization:
        raise HTTPException(status_code=404, detail="No organization associated with user")
        
    settings = db.query(OrganizationSettings).filter(OrganizationSettings.organization_id == organization.id).first()
    
    if not settings:
        settings = OrganizationSettings(organization_id=organization.id)
        db.add(settings)
        
    if "timezone" in payload:
        settings.timezone = payload["timezone"]
    if "ai_enabled" in payload:
        settings.ai_enabled = payload["ai_enabled"]
    if "parent_enabled" in payload:
        settings.parent_enabled = payload["parent_enabled"]
    if "counselor_enabled" in payload:
        settings.counselor_enabled = payload["counselor_enabled"]
        
    db.commit()
    db.refresh(settings)
    return settings
