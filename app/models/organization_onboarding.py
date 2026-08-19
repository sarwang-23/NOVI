from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.database.base import Base

class OrganizationOnboarding(Base):
    __tablename__ = "organization_onboardings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # User who initiated the onboarding
    initiated_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # draft, in_progress, pending_review, approved, active, rejected, suspended
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    
    current_step: Mapped[str] = mapped_column(String(50), nullable=False, default="organization_information")
    completed_steps: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    
    metadata_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
