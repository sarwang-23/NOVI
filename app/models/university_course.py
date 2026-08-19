from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UniversityCourse(Base):
    __tablename__ = "university_courses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    university_id: Mapped[int] = mapped_column(
        ForeignKey("universities.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    degree_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    duration: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    entry_requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    tuition: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
