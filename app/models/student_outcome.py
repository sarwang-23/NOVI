from datetime import datetime, date

from sqlalchemy import ForeignKey, String, Text, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.database.base import Base


class StudentOutcome(Base):
    __tablename__ = "student_outcomes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    outcome_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False  # e.g., 'admission', 'scholarship', 'job_offer', 'certification'
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    achieved_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    metadata_dict: Mapped[dict | None] = mapped_column(
        JSONB,
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
