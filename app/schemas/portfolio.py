from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AchievementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=100)
    organization: Optional[str] = Field(default=None, max_length=255)
    achievement_date: Optional[str] = None
    skills: Optional[str] = Field(default=None, max_length=2000)


class AchievementUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=100)
    organization: Optional[str] = Field(default=None, max_length=255)
    achievement_date: Optional[str] = None
    skills: Optional[str] = Field(default=None, max_length=2000)


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    role: Optional[str] = Field(default=None, max_length=100)
    skills: Optional[str] = Field(default=None, max_length=2000)
    outcome: Optional[str] = Field(default=None, max_length=2000)
    evidence: Optional[str] = Field(default=None, max_length=2000)


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    role: Optional[str] = Field(default=None, max_length=100)
    skills: Optional[str] = Field(default=None, max_length=2000)
    outcome: Optional[str] = Field(default=None, max_length=2000)
    evidence: Optional[str] = Field(default=None, max_length=2000)


class CertificateCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    organization: Optional[str] = Field(default=None, max_length=255)
    issue_date: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=100)
    file_url: Optional[str] = Field(default=None, max_length=2000)


class CertificateUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    organization: Optional[str] = Field(default=None, max_length=255)
    issue_date: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=100)
    file_url: Optional[str] = Field(default=None, max_length=2000)
