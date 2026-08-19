from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.models.audit import AuditLog

router = APIRouter(
    prefix="/api/v1/admin/audit",
    tags=["Admin Audit"]
)

@router.get("")
def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user = Depends(require_permission("audit.read")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    
    if organization:
        query = query.filter(AuditLog.organization_id == organization.id)
        
    if action:
        query = query.filter(AuditLog.action == action)
        
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
        
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "id": log.id,
                "actor_user_id": log.actor_user_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "created_at": log.created_at
            } for log in logs
        ],
        "skip": skip,
        "limit": limit,
        "total": total
    }
