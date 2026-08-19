from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    auth0_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
