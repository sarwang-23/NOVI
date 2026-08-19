from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class WeeklyCheckin(Base):
    __tablename__ = "weekly_checkins"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    week_start: Mapped[datetime] = mapped_column(
        Date,
        nullable=False
    )

    week_end: Mapped[datetime] = mapped_column(
        Date,
        nullable=False
    )

    accomplishments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    learnings: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    difficulties: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    proud_of: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    improvement_area: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    mood: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
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
