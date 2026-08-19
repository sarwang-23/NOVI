from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Any

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.skill import Skill, StudentSkill

router = APIRouter(
    prefix="/api/v1/skills",
    tags=["Skills"]
)

# --- SCHEMAS ---

class SkillOut(BaseModel):
    id: int
    name: str
    category: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True

class StudentSkillCreate(BaseModel):
    skill_id: int
    level: str = Field(default="beginner", pattern="^(beginner|developing|intermediate|advanced)$")
    evidence: Optional[List[dict]] = None
    source: Optional[str] = None

class StudentSkillUpdate(BaseModel):
    level: Optional[str] = Field(default=None, pattern="^(beginner|developing|intermediate|advanced)$")
    evidence: Optional[List[dict]] = None
    source: Optional[str] = None

class StudentSkillOut(BaseModel):
    id: int
    student_id: int
    skill_id: int
    level: str
    evidence: Optional[List[dict]]
    source: Optional[str]
    skill: Optional[SkillOut] = None

    class Config:
        from_attributes = True

# --- HELPER ---

def _get_student(user, db: Session) -> Student:
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student

# --- ENDPOINTS ---

@router.get("/catalog", response_model=dict)
def get_skill_catalog(
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    if search:
        query = query.filter(Skill.name.ilike(f"%{search}%"))

    total = query.count()
    skills = query.order_by(Skill.name).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "description": s.description
            } for s in skills
        ]
    }

@router.get("/me", response_model=List[StudentSkillOut])
def get_my_skills(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    student = _get_student(user, db)
    
    student_skills = db.query(StudentSkill).filter(StudentSkill.student_id == student.id).all()
    
    result = []
    for ss in student_skills:
        skill = db.query(Skill).filter(Skill.id == ss.skill_id).first()
        result.append({
            "id": ss.id,
            "student_id": ss.student_id,
            "skill_id": ss.skill_id,
            "level": ss.level,
            "evidence": ss.evidence,
            "source": ss.source,
            "skill": {
                "id": skill.id,
                "name": skill.name,
                "category": skill.category,
                "description": skill.description
            } if skill else None
        })
        
    return result

@router.post("/me", status_code=201, response_model=StudentSkillOut)
def add_my_skill(
    payload: StudentSkillCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found in catalog")
        
    # Check if already added
    existing = db.query(StudentSkill).filter(
        StudentSkill.student_id == student.id,
        StudentSkill.skill_id == payload.skill_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Skill already added for this student")
        
    new_skill = StudentSkill(
        student_id=student.id,
        skill_id=payload.skill_id,
        level=payload.level,
        evidence=payload.evidence,
        source=payload.source
    )
    
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    
    return {
        "id": new_skill.id,
        "student_id": new_skill.student_id,
        "skill_id": new_skill.skill_id,
        "level": new_skill.level,
        "evidence": new_skill.evidence,
        "source": new_skill.source,
        "skill": {
            "id": skill.id,
            "name": skill.name,
            "category": skill.category,
            "description": skill.description
        }
    }

@router.patch("/me/{student_skill_id}", response_model=StudentSkillOut)
def update_my_skill(
    student_skill_id: int,
    payload: StudentSkillUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    ss = db.query(StudentSkill).filter(
        StudentSkill.id == student_skill_id,
        StudentSkill.student_id == student.id
    ).first()
    
    if not ss:
        raise HTTPException(status_code=404, detail="Student skill not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ss, key, value)
        
    db.commit()
    db.refresh(ss)
    
    skill = db.query(Skill).filter(Skill.id == ss.skill_id).first()
    
    return {
        "id": ss.id,
        "student_id": ss.student_id,
        "skill_id": ss.skill_id,
        "level": ss.level,
        "evidence": ss.evidence,
        "source": ss.source,
        "skill": {
            "id": skill.id,
            "name": skill.name,
            "category": skill.category,
            "description": skill.description
        } if skill else None
    }

@router.delete("/me/{student_skill_id}")
def delete_my_skill(
    student_skill_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    
    ss = db.query(StudentSkill).filter(
        StudentSkill.id == student_skill_id,
        StudentSkill.student_id == student.id
    ).first()
    
    if not ss:
        raise HTTPException(status_code=404, detail="Student skill not found")
        
    db.delete(ss)
    db.commit()
    
    return {"success": True, "message": "Student skill removed successfully"}
