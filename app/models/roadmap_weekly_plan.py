from datetime import datetime, date

from sqlalchemy import ForeignKey, String, Text, DateTime, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.database.base import Base


class WeeklyPlan(Base):
    __tablename__ = "roadmap_weekly_plans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    monthly_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("roadmap_monthly_plans.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    week_start: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    week_end: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    objectives: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium"  # low, medium, high
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="planned"  # planned, active, completed, skipped
    )

    progress_percent: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
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

    generated_by: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )


class WeeklyPlanItem(Base):
    __tablename__ = "roadmap_weekly_plan_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    weekly_plan_id: Mapped[int] = mapped_column(
        ForeignKey("roadmap_weekly_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    source_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True  # e.g., 'goal', 'roadmap_milestone', 'task'
    )

    source_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium"
    )

    estimated_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"  # pending, in_progress, completed, skipped, rescheduled
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
