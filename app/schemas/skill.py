from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentSkillCreate(BaseModel):
    skill_id: int
    level: str = Field(default="beginner", pattern="^(beginner|developing|intermediate|advanced)$")
    evidence: Optional[dict] = None
    source: Optional[str] = Field(default=None, max_length=100)


class StudentSkillUpdate(BaseModel):
    level: Optional[str] = Field(default=None, pattern="^(beginner|developing|intermediate|advanced)$")
    evidence: Optional[dict] = None
    source: Optional[str] = Field(default=None, max_length=100)


class SkillOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class StudentSkillOut(BaseModel):
    id: int
    student_id: int
    skill_id: int
    level: str
    evidence: Optional[dict] = None
    source: Optional[str] = None
    last_updated: Optional[datetime] = None
    skill: Optional[SkillOut] = None
