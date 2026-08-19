from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        index=True
    )

    roadmap_id: Mapped[int | None] = mapped_column(
        ForeignKey("roadmaps.id"),
        nullable=True,
        index=True
    )

    milestone_id: Mapped[int | None] = mapped_column(
        ForeignKey("milestones.id"),
        nullable=True,
        index=True
    )

    year_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("roadmap_year_plans.id"),
        nullable=True,
        index=True
    )

    monthly_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("roadmap_monthly_plans.id"),
        nullable=True,
        index=True
    )

    weekly_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("roadmap_weekly_plans.id"),
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

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"  # pending, in_progress, completed, skipped
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium"  # low, medium, high
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

