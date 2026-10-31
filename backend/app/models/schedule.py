"""Modelos SQLAlchemy — horários, atribuições, indisponibilidades e contestações."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.school import Class, Disciplina, Professor, Sala
    from app.models.user import Teacher, User

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


class ScheduleVersion(Base):
    """Versão de um horário (rascunho, publicado, arquivado)."""

    __tablename__ = "schedule_versions"

    id: Mapped[IntPK]
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    # Status: draft, published, archived
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    # Solver usado: cp_sat, tabu_search, simulated_annealing
    solver_used: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Score do horário (quanto maior, melhor)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Número de violações duras (0 se viável)
    hard_violations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Número de penalidades moles
    soft_penalties: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[CreatedAt]
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relacionamentos
    assignments: Mapped[list["ScheduleAssignment"]] = relationship(
        "ScheduleVersion", back_populates="assignments", cascade="all, delete-orphan"
    )


class ScheduleAssignment(Base):
    """Uma atribuição única no horário: turma, disciplina, professor, sala, slot."""

    __tablename__ = "schedule_assignments"

    id: Mapped[IntPK]
    version_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_versions.id"), nullable=False, index=True
    )
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id"), nullable=False, index=True
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"), nullable=False, index=True
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id"), nullable=False, index=True
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"), nullable=False, index=True
    )
    # Slot: {"dia": "segunda", "hora": 1}
    slot: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    version: Mapped["ScheduleVersion"] = relationship(ScheduleVersion, back_populates="assignments")
    class_: Mapped[Class] = relationship(Class, back_populates="assignments")
    subject: Mapped[Disciplina] = relationship(Disciplina, back_populates="assignments")
    teacher: Mapped[Professor] = relationship(Teacher, back_populates="assignments")
    room: Mapped[Sala] = relationship(Sala, back_populates="assignments")
    disputes: Mapped[list["Dispute"]] = relationship(
        "Dispute", back_populates="assignment", cascade="all, delete-orphan"
    )


class Unavailability(Base):
    """Indisponibilidade de um docente em um slot específico."""

    __tablename__ = "unavailabilities"

    id: Mapped[IntPK]
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id"), nullable=False, index=True
    )
    # Slot: {"dia": "segunda", "hora": 1}
    slot: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Justificação pré-definida: deslocamento, folga, almoço, compromisso, doença, outro
    justification: Mapped[str] = mapped_column(String(100), nullable=False)
    # Motivo livre (opcional)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    teacher: Mapped[Teacher] = relationship(Teacher, back_populates="unavailabilities")


class Dispute(Base):
    """Contestação de um docente sobre um slot atribuído."""

    __tablename__ = "disputes"

    id: Mapped[IntPK]
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id"), nullable=False, index=True
    )
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_assignments.id"), nullable=False, index=True
    )
    # Motivo da contestação
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    # Justificação pré-definida
    justification: Mapped[str] = mapped_column(String(100), nullable=False)
    # Estado: pending, accepted, rejected
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    created_at: Mapped[CreatedAt]
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    # Relacionamentos
    teacher: Mapped[Teacher] = relationship(Teacher, back_populates="disputes")
    assignment: Mapped[ScheduleAssignment] = relationship(
        ScheduleAssignment, back_populates="disputes"
    )
    resolver: Mapped[User | None] = relationship(User, foreign_keys=[resolved_by])