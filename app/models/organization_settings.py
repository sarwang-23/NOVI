from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class OrganizationSettings(Base):
    __tablename__ = "organization_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    timezone: Mapped[str] = mapped_column(String(100), nullable=False, default="UTC")
    academic_year: Mapped[str | None] = mapped_column(String(50), nullable=True)
    curriculum: Mapped[str | None] = mapped_column(String(100), nullable=True)
    grading_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    default_language: Mapped[str] = mapped_column(String(20), nullable=False, default="en")
    
    # Feature flags
    ai_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    parent_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    counselor_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
