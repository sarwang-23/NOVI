from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.database.base import Base


class RoadmapYearPlan(Base):
    __tablename__ = "roadmap_year_plans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    roadmap_id: Mapped[int] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    academic_year: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    grade: Mapped[int | None] = mapped_column(
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

    academic_objectives: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    career_objectives: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    university_objectives: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    personal_objectives: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="planned"  # planned, active, completed, archived
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
