from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentProfileUpdate(BaseModel):
    grade: Optional[int] = Field(default=None, ge=1, le=12)
    school: Optional[str] = Field(default=None, max_length=255)
    curriculum: Optional[str] = Field(default=None, max_length=100)


class StudentOut(BaseModel):
    id: int
    user_id: int
    grade: Optional[int] = None
    school: Optional[str] = None
    curriculum: Optional[str] = None
    organization_id: Optional[int] = None
