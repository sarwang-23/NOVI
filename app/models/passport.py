from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, Integer, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CareerPassport(Base):
    __tablename__ = "career_passports"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        unique=True,
        index=True
    )

    about_me: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    interests: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    work_style: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    learning_style: Mapped[str | None] = mapped_column(
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

