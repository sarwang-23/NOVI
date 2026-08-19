from datetime import datetime

from sqlalchemy import ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CareerSkill(Base):
    __tablename__ = "career_skills"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    career_id: Mapped[int] = mapped_column(
        ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    importance: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class CareerSubject(Base):
    __tablename__ = "career_subjects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    career_id: Mapped[int] = mapped_column(
        ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    importance: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
