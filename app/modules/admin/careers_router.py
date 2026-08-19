from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.core.rbac import require_permission
from app.models.career import Career

router = APIRouter(
    prefix="/api/v1/admin/careers",
    tags=["Admin Careers"]
)

@router.get("")
def get_admin_careers(
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user = Depends(require_permission("careers.read")),
    db: Session = Depends(get_db)
):
    query = db.query(Career)
    
    if search:
        query = query.filter(Career.name.ilike(f"%{search}%"))
        
    total = query.count()
    careers = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "is_active": c.is_active
            } for c in careers
        ],
        "skip": skip,
        "limit": limit,
        "total": total
    }

@router.post("/{career_id}/publish")
def publish_career(
    career_id: int,
    admin_user = Depends(require_permission("careers.write")),
    db: Session = Depends(get_db)
):
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
        
    career.is_active = True
    db.commit()
    return {"message": "Career published"}

@router.post("/{career_id}/unpublish")
def unpublish_career(
    career_id: int,
    admin_user = Depends(require_permission("careers.write")),
    db: Session = Depends(get_db)
):
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
        
    career.is_active = False
    db.commit()
    return {"message": "Career unpublished"}
