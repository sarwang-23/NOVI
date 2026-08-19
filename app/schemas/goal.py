from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GoalCreate(BaseModel):
    goal_type: str = Field(..., pattern="^(career|university|academic|personal)$")
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    target: Optional[str] = Field(default=None, max_length=255)


class GoalUpdate(BaseModel):
    goal_type: Optional[str] = Field(default=None, pattern="^(career|university|academic|personal)$")
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    target: Optional[str] = Field(default=None, max_length=255)


class GoalOut(BaseModel):
    id: int
    student_id: int
    goal_type: str
    title: str
    description: Optional[str] = None
    target: Optional[str] = None
    status: str
    created_at: datetime
