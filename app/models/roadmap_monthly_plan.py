from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.database.base import Base


class MonthlyPlan(Base):
    __tablename__ = "roadmap_monthly_plans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    year_plan_id: Mapped[int] = mapped_column(
        ForeignKey("roadmap_year_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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
