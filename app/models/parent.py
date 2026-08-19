from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class Parent(Base):
    __tablename__ = "parents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    
    relationship_status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ParentStudent(Base):
    __tablename__ = "parent_students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False, default="parent") # parent, guardian, other
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active") # pending, active, revoked
    
    invited_by: Mapped[str] = mapped_column(String(50), nullable=True) # "parent" or "student"

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ParentStudentInvitation(Base):
    __tablename__ = "parent_student_invitations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), nullable=True, index=True)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True)
    
    token: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending") # pending, accepted, rejected, expired

    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
