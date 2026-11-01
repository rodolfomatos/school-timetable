"""Modelos SQLAlchemy — horários, atribuições, indisponibilidades e contestações."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
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
from app.models.school import Class, Room, Subject, Teacher
from app.models.user import User

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
        "ScheduleAssignment", back_populates="version", cascade="all, delete-orphan"
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
    subject: Mapped[Subject] = relationship(Subject, back_populates="assignments")
    teacher: Mapped[Teacher] = relationship(Teacher, back_populates="assignments")
    room: Mapped[Room] = relationship(Room, back_populates="assignments")
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


class SolverJobStatus(str):
    """Estados possíveis de um job de solver."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT_WITH_INCUMBENT = "timeout_with_incumbent"
    TIMEOUT_NO_SOLUTION = "timeout_no_solution"


class SolverJob(Base):
    """Job de execução do solver com persistência e ciclo de vida completo."""

    __tablename__ = "solver_jobs"

    id: Mapped[UUIDPK]
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    # Estado do job
    status: Mapped[str] = mapped_column(String(50), default=SolverJobStatus.PENDING, nullable=False)
    # Solver solicitado: cp_sat, tabu_search, simulated_annealing
    solver: Mapped[str] = mapped_column(String(50), nullable=False)
    # Limite de tempo em segundos
    time_limit_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    # Indisponibilidades adicionais passadas na request (JSON)
    additional_unavailabilities: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    # Referência à versão do horário gerada (se concluído com sucesso)
    schedule_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("schedule_versions.id"), nullable=True, index=True
    )
    # Score final (None se falhou/sem solução)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Violações duras
    hard_violations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Penalidades moles
    soft_penalties: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Mensagem de erro (se falhou)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Tempo de execução em segundos
    elapsed_seconds: Mapped[float | None] = mapped_column(nullable=True)
    # Semente aleatória usada
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Parâmetros do solver (JSON)
    solver_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Resultado bruto do solver (para debug/auditoria)
    raw_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # ID do utilizador que iniciou o job
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[CreatedAt]
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    schedule_version: Mapped["ScheduleVersion | None"] = relationship("ScheduleVersion")
    creator: Mapped["User | None"] = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<SolverJob(id={self.id}, status={self.status}, solver={self.solver})>"