from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    roadmap_id: Optional[int] = None
    milestone_id: Optional[int] = None
    priority: str = Field(default="medium", min_length=1, max_length=50)
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[str] = Field(default=None, min_length=1, max_length=50)
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(default=None, min_length=1, max_length=50)


class TaskOut(BaseModel):
    id: int
    student_id: int
    roadmap_id: Optional[int] = None
    milestone_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
