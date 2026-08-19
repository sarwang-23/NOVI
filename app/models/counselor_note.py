from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class CounselorNote(Base):
    __tablename__ = "counselor_notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    counselor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    note: Mapped[str] = mapped_column(Text, nullable=False)
    
    # counselor_private, organization_visible, student_visible, parent_visible
    visibility: Mapped[str] = mapped_column(String(50), nullable=False, default="counselor_private")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
