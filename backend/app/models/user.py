"""Modelos SQLAlchemy — utilizadores, autenticação e papéis."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:  # noqa: F401
    from app.models.school import Teacher, Unavailability, Dispute

IntPK = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
UUIDPK = Annotated[
    str,
    mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())),
]
CreatedAt = Annotated[
    datetime, mapped_column(DateTime(timezone=True), default=datetime.utcnow)
]
UpdatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    ),
]


class Role(str):
    """Papéis de utilizador no sistema."""

    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    COORDINATOR = "coordinator"


class User(Base):
    """Utilizador do sistema (docente, admin, estudante, coordenador)."""

    __tablename__ = "users"

    id: Mapped[IntPK]
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default=Role.STUDENT, nullable=False)
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    teacher_profile: Mapped["Teacher | None"] = relationship(
        "Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    unavailabilities: Mapped[list["Unavailability"]] = relationship(
        "Unavailability", back_populates="teacher", cascade="all, delete-orphan"
    )
    disputes: Mapped[list["Dispute"]] = relationship(
        "Dispute", back_populates="teacher", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
