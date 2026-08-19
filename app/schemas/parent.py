from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InviteStudentRequest(BaseModel):
    student_email: str
    relationship_type: Optional[str] = "parent"


class AcceptInviteRequest(BaseModel):
    token: str
