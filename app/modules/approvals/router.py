from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_role, get_current_organization
from app.models.approval_request import ApprovalRequest
from datetime import datetime

router = APIRouter(
    prefix="/api/v1/organization/approvals",
    tags=["Approvals"]
)

@router.post("")
def create_approval_request(
    payload: dict,
    admin = Depends(require_role(["organization_admin", "super_admin"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    request = ApprovalRequest(
        organization_id=organization.id,
        requested_by=admin.id,
        action=payload.get("action"),
        resource_type=payload.get("resource_type"),
        resource_id=payload.get("resource_id"),
        reason=payload.get("reason")
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

@router.post("/{approval_id}/approve")
def approve_request(
    approval_id: int,
    admin = Depends(require_role(["super_admin"])), # Only super admins can approve enterprise actions for now
    db: Session = Depends(get_db)
):
    request = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Approval request not found")
        
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Request is not pending")
        
    if request.requested_by == admin.id:
        raise HTTPException(status_code=403, detail="Cannot approve your own request (Separation of Duties)")
        
    request.status = "approved"
    request.approved_by = admin.id
    request.resolved_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Request approved", "approval_id": approval_id}
