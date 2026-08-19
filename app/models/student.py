from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    grade: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    school: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    curriculum: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
