from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoadmapCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    current_grade: Optional[int] = Field(default=None, ge=1, le=12)
    target_grade: Optional[int] = Field(default=None, ge=1, le=12)


class RoadmapUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    current_grade: Optional[int] = Field(default=None, ge=1, le=12)
    target_grade: Optional[int] = Field(default=None, ge=1, le=12)


class RoadmapOut(BaseModel):
    id: int
    student_id: int
    title: str
    description: Optional[str] = None
    current_grade: Optional[int] = None
    target_grade: Optional[int] = None
    status: str
    created_at: datetime
