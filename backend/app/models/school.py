"""Modelos SQLAlchemy — entidades da escola (salas, disciplinas, turmas, cursos, professores)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:  # noqa: F401
    from app.models.schedule import ScheduleAssignment, Unavailability, Dispute
    from app.models.user import User

IntPK = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
UUIDPK = Annotated[
    str,
    mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())),
]
CreatedAt = Annotated[
    datetime, mapped_column(DateTime(timezone=True), default=datetime.utcnow)
]


class Course(Base):
    """Curso / departamento da instituição."""

    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("code", "institution_id", name="uq_courses_code_institution"),
    )

    id: Mapped[IntPK]
    code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="course")
    classes: Mapped[list["Class"]] = relationship("Class", back_populates="course")
    subjects: Mapped[list["Subject"]] = relationship("Subject", back_populates="course")


class Room(Base):
    """Sala de aula / laboratório / espaço específico."""

    __tablename__ = "rooms"

    id: Mapped[IntPK]
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), default="normal", nullable=False)
    # Cursos que podem usar esta sala (JSON array de códigos)
    allowed_courses: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    # Slots já reservados para outras atividades (JSON array de {"dia": "segunda", "hora": 1})
    reserved_times: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    # Tempo de setup antes da aula (minutos)
    setup_before: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Tempo de limpeza depois da aula (minutos)
    cleanup_after: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id"), nullable=True, index=True
    )
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    course: Mapped["Course | None"] = relationship("Course", back_populates="rooms")
    assignments: Mapped[list["ScheduleAssignment"]] = relationship(
        "ScheduleAssignment", back_populates="room"
    )


class Subject(Base):
    """Disciplina / matéria."""

    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("code", "institution_id", name="uq_subjects_code_institution"),
    )

    id: Mapped[IntPK]
    code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    weekly_load: Mapped[int] = mapped_column(Integer, nullable=False)
    # Tipo de sala requerida (normal, laboratorio, anatomia)
    room_type_required: Mapped[str] = mapped_column(String(50), default="normal", nullable=False)
    # Periodicidade: semanal, quinzenal, modulo_semestre
    periodicity: Mapped[str] = mapped_column(String(50), default="semanal", nullable=False)
    # Semanas em que a disciplina ocorre (JSON array de números de semana)
    weeks_active: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    course: Mapped["Course"] = relationship("Course", back_populates="subjects")
    assignments: Mapped[list["ScheduleAssignment"]] = relationship(
        "ScheduleAssignment", back_populates="subject"
    )
    class_links: Mapped[list["ClassSubject"]] = relationship(
        "ClassSubject", back_populates="subject", cascade="all, delete-orphan"
    )
    teacher_links: Mapped[list["TeacherSubject"]] = relationship(
        "TeacherSubject", back_populates="subject", cascade="all, delete-orphan"
    )


class Class(Base):
    """Turma / classe de estudantes."""

    __tablename__ = "classes"

    id: Mapped[IntPK]
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    student_count: Mapped[int] = mapped_column(Integer, nullable=False)
    # Semanas em que a turma está ativa (JSON array)
    weeks_active: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    course: Mapped["Course"] = relationship("Course", back_populates="classes")
    assignments: Mapped[list["ScheduleAssignment"]] = relationship(
        "ScheduleAssignment", back_populates="class_"
    )
    subject_links: Mapped[list["ClassSubject"]] = relationship(
        "ClassSubject", back_populates="class_", cascade="all, delete-orphan"
    )


class Teacher(Base):
    """Perfil de docente associado a um utilizador."""

    __tablename__ = "teachers"

    id: Mapped[IntPK]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False, index=True
    )
    employee_code: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    # Dia de folga preferido (ex: "sexta")
    day_off_preferred: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Prefere manhã (True) ou tarde (False)
    morning_preferred: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Almoço sagrado (não agendar nesse intervalo)
    lunch_sacred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Tempo de deslocamento entre instituições (minutos)
    commute_time: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Disponibilidade por slot (JSON: {"segunda": [1,2,3], "terca": [...]})
    availability: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    user: Mapped["User"] = relationship("User", back_populates="teacher_profile")
    unavailabilities: Mapped[list["Unavailability"]] = relationship(
        "Unavailability", back_populates="teacher", cascade="all, delete-orphan"
    )
    disputes: Mapped[list["Dispute"]] = relationship(
        "Dispute", back_populates="teacher", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["ScheduleAssignment"]] = relationship(
        "ScheduleAssignment", back_populates="teacher"
    )
    subject_links: Mapped[list["TeacherSubject"]] = relationship(
        "TeacherSubject", back_populates="teacher", cascade="all, delete-orphan"
    )
    class_subject_links: Mapped[list["ClassSubject"]] = relationship(
        "ClassSubject", back_populates="teacher"
    )


class ClassSubject(Base):
    """Relação curricular explícita: uma disciplina leccionada a uma turma.

    ``teacher_id`` é opcional: quando preenchido, fixa o docente responsável;
    quando vazio, o domínio escolhe entre os docentes qualificados.
    """

    __tablename__ = "class_subjects"
    __table_args__ = (
        UniqueConstraint("class_id", "subject_id", "institution_id", name="uq_class_subject_institution"),
    )

    id: Mapped[IntPK]
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id"), nullable=False, index=True
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"), nullable=False, index=True
    )
    teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"), nullable=True, index=True
    )
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    class_: Mapped["Class"] = relationship("Class", back_populates="subject_links")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="class_links")
    teacher: Mapped["Teacher | None"] = relationship(
        "Teacher", back_populates="class_subject_links"
    )


class TeacherSubject(Base):
    """Qualificação explícita: docente habilitado a leccionar uma disciplina."""

    __tablename__ = "teacher_subjects"
    __table_args__ = (
        UniqueConstraint("teacher_id", "subject_id", "institution_id", name="uq_teacher_subject_institution"),
    )

    id: Mapped[IntPK]
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id"), nullable=False, index=True
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"), nullable=False, index=True
    )
    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[CreatedAt]

    # Relacionamentos
    teacher: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="subject_links"
    )
    subject: Mapped["Subject"] = relationship(
        "Subject", back_populates="teacher_links"
    )
