from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import List, Optional

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.career import Career

router = APIRouter(
    prefix="/api/v1/careers",
    tags=["Careers"]
)

# --- SCHEMAS ---

class CareerOut(BaseModel):
    id: int
    name: str
    slug: str
    short_description: Optional[str]
    industry: Optional[str]
    education_level: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: Optional[str]
    demand_level: Optional[str]

    class Config:
        from_attributes = True

class CareerDetailOut(CareerOut):
    description: Optional[str]
    future_demand: Optional[str]
    work_environment: Optional[str]

# --- ENDPOINTS ---

@router.get("", response_model=dict)
def get_careers(
    search: Optional[str] = None,
    industry: Optional[str] = None,
    education_level: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Career).filter(Career.is_active == True)

    if search:
        query = query.filter(
            or_(
                Career.name.ilike(f"%{search}%"),
                Career.short_description.ilike(f"%{search}%")
            )
        )
    if industry:
        query = query.filter(Career.industry == industry)
    if education_level:
        query = query.filter(Career.education_level == education_level)

    total = query.count()
    careers = query.order_by(Career.name).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [CareerOut.model_validate(c).model_dump() for c in careers]
    }

@router.get("/{career_id}", response_model=CareerDetailOut)
def get_career_by_id(
    career_id: int,
    db: Session = Depends(get_db)
):
    career = db.query(Career).filter(Career.id == career_id, Career.is_active == True).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
        
    return career
