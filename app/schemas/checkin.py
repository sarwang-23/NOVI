from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CheckinCreate(BaseModel):
    week_start: str
    week_end: str
    accomplishments: Optional[str] = None
    learnings: Optional[str] = None
    difficulties: Optional[str] = None
    proud_of: Optional[str] = None
    improvement_area: Optional[str] = None
    mood: Optional[str] = None


class CheckinUpdate(BaseModel):
    accomplishments: Optional[str] = None
    learnings: Optional[str] = None
    difficulties: Optional[str] = None
    proud_of: Optional[str] = None
    improvement_area: Optional[str] = None
    mood: Optional[str] = None
    completed: Optional[bool] = None
