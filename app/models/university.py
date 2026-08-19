from datetime import datetime

from sqlalchemy import String, Text, DateTime, Boolean, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    country: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    ranking: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    acceptance_rate: Mapped[Numeric | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    tuition_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    tuition_max: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
