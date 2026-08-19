from datetime import datetime, date

from sqlalchemy import ForeignKey, String, Text, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.database.base import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    opportunity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    provider: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    deadline: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    eligibility: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    skills: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    interests: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active"  # active, archived, closed
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class StudentOpportunity(Base):
    __tablename__ = "student_opportunities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    opportunity_id: Mapped[int] = mapped_column(
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="viewed"  # viewed, saved, dismissed, applied, completed
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
