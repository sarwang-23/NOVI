from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_role, get_current_organization
from app.models.organization import Organization, OrganizationMembership
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/organizations",
    tags=["Organizations"]
)

@router.get("/me")
def get_my_organization(
    # Only users with an admin or counselor role typically manage organization details directly
    admin_user = Depends(require_role(["organization_admin", "super_admin"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not organization:
        raise HTTPException(status_code=404, detail="User is not associated with any organization")
        
    return {
        "id": organization.id,
        "name": organization.name,
        "slug": organization.slug,
        "type": organization.organization_type,
        "status": organization.status
    }

@router.get("/me/members")
def get_organization_members(
    admin_user = Depends(require_role(["organization_admin", "super_admin"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not organization:
        raise HTTPException(status_code=404, detail="User is not associated with any organization")
        
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == organization.id
    ).all()
    
    results = []
    for m in memberships:
        u = db.query(User).filter(User.id == m.user_id).first()
        results.append({
            "membership_id": m.id,
            "user_id": u.id if u else None,
            "email": u.email if u else None,
            "role": m.role,
            "status": m.status
        })
        
    return {"items": results}
