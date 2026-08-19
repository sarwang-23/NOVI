from datetime import datetime

from sqlalchemy import String, Text, DateTime, Boolean, Integer, Numeric, ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

# Many-to-Many association table for Career <-> CareerCategory
career_category_link = Table(
    "career_category_link",
    Base.metadata,
    Column("career_id", Integer, ForeignKey("careers.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("career_categories.id"), primary_key=True),
)

class Career(Base):
    __tablename__ = "careers"

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

    short_description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    industry: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    education_level: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    salary_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    salary_max: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    salary_currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    demand_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    future_demand: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    work_environment: Mapped[str | None] = mapped_column(
        Text,
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

    # Relationships
    categories = relationship(
        "CareerCategory",
        secondary=career_category_link,
        backref="careers"
    )
