from datetime import datetime, date

from sqlalchemy import ForeignKey, String, Text, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    university_id: Mapped[int | None] = mapped_column(
        ForeignKey("universities.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    program_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft"  # draft, planning, in_progress, ready, submitted, accepted, rejected, waitlisted, enrolled
    )

    target_term: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    application_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True  # e.g., 'early_decision', 'early_action', 'regular'
    )

    application_deadline: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
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


class ApplicationRequirement(Base):
    __tablename__ = "application_requirements"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
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

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"  # pending, in_progress, completed, waived
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
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
