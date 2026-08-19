from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class ApplicationCreate(BaseModel):
    university_id: Optional[int] = None
    program_name: str
    target_term: Optional[str] = None
    application_type: Optional[str] = None
    application_deadline: Optional[date] = None


class ApplicationUpdate(BaseModel):
    program_name: Optional[str] = None
    target_term: Optional[str] = None
    application_type: Optional[str] = None
    application_deadline: Optional[date] = None
    status: Optional[str] = Field(
        default=None,
        pattern="^(draft|planning|in_progress|ready|submitted|accepted|rejected|waitlisted|enrolled)$",
    )


class ApplicationRequirementCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None


class ApplicationRequirementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = Field(
        default=None, pattern="^(pending|in_progress|completed|waived)$"
    )


class OutcomeCreate(BaseModel):
    outcome_type: str = Field(
        ..., pattern="^(admission|scholarship|job_offer|certification)$"
    )
    title: str
    description: Optional[str] = None
    achieved_at: Optional[date] = None
    source: Optional[str] = None


class OutcomeUpdate(BaseModel):
    outcome_type: Optional[str] = Field(
        default=None,
        pattern="^(admission|scholarship|job_offer|certification)$",
    )
    title: Optional[str] = None
    description: Optional[str] = None
    achieved_at: Optional[date] = None
    source: Optional[str] = None
