from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import List, Optional

from app.database.connection import get_db
from app.models.university import University
from app.models.university_course import UniversityCourse

router = APIRouter(
    prefix="/api/v1/universities",
    tags=["Universities"]
)

# --- SCHEMAS ---

class UniversityOut(BaseModel):
    id: int
    name: str
    slug: str
    country: Optional[str]
    city: Optional[str]
    ranking: Optional[int]
    acceptance_rate: Optional[float]
    tuition_min: Optional[int]
    tuition_max: Optional[int]
    currency: Optional[str]

    class Config:
        from_attributes = True

class UniversityDetailOut(UniversityOut):
    description: Optional[str]
    website: Optional[str]
    location: Optional[str]

class UniversityCourseOut(BaseModel):
    id: int
    university_id: int
    name: str
    degree_type: Optional[str]
    duration: Optional[str]
    description: Optional[str]
    entry_requirements: Optional[str]
    tuition: Optional[int]
    currency: Optional[str]

    class Config:
        from_attributes = True

# --- ENDPOINTS ---

@router.get("", response_model=dict)
def get_universities(
    search: Optional[str] = None,
    country: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(University).filter(University.is_active == True)

    if search:
        query = query.filter(
            or_(
                University.name.ilike(f"%{search}%"),
                University.city.ilike(f"%{search}%"),
                University.country.ilike(f"%{search}%")
            )
        )
    if country:
        query = query.filter(University.country == country)

    total = query.count()
    universities = query.order_by(University.ranking.asc().nullslast(), University.name).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [UniversityOut.model_validate(u).model_dump() for u in universities]
    }

@router.get("/compare", response_model=List[UniversityOut])
def compare_universities(
    ids: str = Query(..., description="Comma separated list of university IDs"),
    db: Session = Depends(get_db)
):
    try:
        id_list = [int(i.strip()) for i in ids.split(",") if i.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not id_list:
        return []

    universities = db.query(University).filter(University.id.in_(id_list), University.is_active == True).all()
    return universities

@router.get("/{university_id}", response_model=UniversityDetailOut)
def get_university_by_id(
    university_id: int,
    db: Session = Depends(get_db)
):
    university = db.query(University).filter(University.id == university_id, University.is_active == True).first()
    if not university:
        raise HTTPException(status_code=404, detail="University not found")
        
    return university

@router.get("/{university_id}/courses", response_model=dict)
def get_university_courses(
    university_id: int,
    degree_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    university = db.query(University).filter(University.id == university_id, University.is_active == True).first()
    if not university:
        raise HTTPException(status_code=404, detail="University not found")

    query = db.query(UniversityCourse).filter(UniversityCourse.university_id == university_id)
    if degree_type:
        query = query.filter(UniversityCourse.degree_type == degree_type)

    total = query.count()
    courses = query.order_by(UniversityCourse.name).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [UniversityCourseOut.model_validate(c).model_dump() for c in courses]
    }
