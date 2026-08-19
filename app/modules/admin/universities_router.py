from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.core.rbac import require_permission
from app.models.university import University

router = APIRouter(
    prefix="/api/v1/admin/universities",
    tags=["Admin Universities"]
)

@router.get("")
def get_admin_universities(
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user = Depends(require_permission("universities.read")),
    db: Session = Depends(get_db)
):
    query = db.query(University)
    
    if search:
        query = query.filter(University.name.ilike(f"%{search}%"))
        
    total = query.count()
    universities = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "id": u.id,
                "name": u.name,
                "slug": u.slug,
                "country": u.country,
                "is_active": u.is_active
            } for u in universities
        ],
        "skip": skip,
        "limit": limit,
        "total": total
    }

@router.post("/{university_id}/publish")
def publish_university(
    university_id: int,
    admin_user = Depends(require_permission("universities.write")),
    db: Session = Depends(get_db)
):
    university = db.query(University).filter(University.id == university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="University not found")
        
    university.is_active = True
    db.commit()
    return {"message": "University published"}

@router.post("/{university_id}/unpublish")
def unpublish_university(
    university_id: int,
    admin_user = Depends(require_permission("universities.write")),
    db: Session = Depends(get_db)
):
    university = db.query(University).filter(University.id == university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="University not found")
        
    university.is_active = False
    db.commit()
    return {"message": "University unpublished"}
