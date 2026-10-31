"""Testes de integridade do modelo ORM e CRUD relacional.

Cobrem o defeito corrigido no T049: o grafo de relações SQLAlchemy não
configurava (``configure_mappers()`` falhava) e, portanto, nenhuma operação
real sobre a base de dados era possível.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import configure_mappers, selectinload

from app.db.base import Base
from app.models.schedule import (
    Dispute,
    ScheduleAssignment,
    ScheduleVersion,
    Unavailability,
)
from app.models.school import Class, Course, Room, Subject, Teacher
from app.models.user import Role, User


def test_mappers_configure_without_error() -> None:
    """O grafo de relações tem de configurar sem ambiguidade."""

    configure_mappers()


@pytest.fixture
async def session() -> AsyncSession:
    """Sessão assíncrona sobre SQLite em memória, com schema criado."""

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        yield db

    await engine.dispose()


async def test_crud_and_relationships(session: AsyncSession) -> None:
    """Cria, lê, atualiza e apaga entidades relacionadas de ponta a ponta."""

    course = Course(code="ENF", name="Enfermagem")
    room = Room(name="Sala 1", capacity=30, room_type="normal", course=course)
    subject = Subject(
        code="ANA",
        name="Anatomia",
        weekly_load=4,
        room_type_required="laboratorio",
        course=course,
    )
    school_class = Class(name="Turma A", year=1, student_count=28, course=course)
    user = User(
        email="docente@example.test",
        hashed_password="x",
        full_name="Docente Sintético",
        role=Role.TEACHER,
    )
    teacher = Teacher(user=user, employee_code="DOC-001", commute_time=15)
    session.add_all([course, room, subject, school_class, user, teacher])
    await session.commit()

    # Leitura e relações inversas (eager loading explícito para async)
    loaded_course = (
        await session.execute(
            select(Course)
            .where(Course.code == "ENF")
            .options(
                selectinload(Course.rooms),
                selectinload(Course.subjects),
                selectinload(Course.classes),
            )
        )
    ).scalar_one()
    assert loaded_course.rooms == [room]
    assert loaded_course.subjects == [subject]
    assert loaded_course.classes == [school_class]

    loaded_teacher = (
        await session.execute(
            select(Teacher)
            .where(Teacher.employee_code == "DOC-001")
            .options(selectinload(Teacher.user))
        )
    ).scalar_one()
    assert loaded_teacher.user is user

    loaded_user = (
        await session.execute(
            select(User)
            .where(User.email == "docente@example.test")
            .options(selectinload(User.teacher_profile))
        )
    ).scalar_one()
    assert loaded_user.teacher_profile is loaded_teacher

    # Horário e atribuição
    version = ScheduleVersion(status="draft", solver_used="cp_sat", score=10)
    assignment = ScheduleAssignment(
        version=version,
        class_=school_class,
        subject=subject,
        teacher=teacher,
        room=room,
        slot={"dia": "segunda", "hora": 1},
    )
    session.add(assignment)
    await session.commit()

    loaded_assignment = (
        await session.execute(
            select(ScheduleAssignment)
            .where(ScheduleAssignment.id == assignment.id)
            .options(
                selectinload(ScheduleAssignment.version).selectinload(
                    ScheduleVersion.assignments
                ),
                selectinload(ScheduleAssignment.class_),
                selectinload(ScheduleAssignment.subject),
                selectinload(ScheduleAssignment.teacher),
                selectinload(ScheduleAssignment.room),
            )
        )
    ).scalar_one()
    assert loaded_assignment.version is version
    assert loaded_assignment.class_ is school_class
    assert loaded_assignment.subject is subject
    assert loaded_assignment.teacher is teacher
    assert loaded_assignment.room is room
    assert version.assignments == [loaded_assignment]

    # Update
    loaded_assignment.slot = {"dia": "terca", "hora": 2}
    await session.commit()
    assert loaded_assignment.slot == {"dia": "terca", "hora": 2}

    # Indisponibilidade e contestação
    unavailability = Unavailability(
        teacher=teacher,
        slot={"dia": "sexta", "hora": 8},
        justification="folga",
    )
    dispute = Dispute(
        teacher=teacher,
        assignment=loaded_assignment,
        reason="Conflito com outra instituição",
        justification="deslocamento",
    )
    session.add_all([unavailability, dispute])
    await session.commit()

    loaded_teacher = (
        await session.execute(
            select(Teacher)
            .where(Teacher.id == teacher.id)
            .options(
                selectinload(Teacher.unavailabilities),
                selectinload(Teacher.disputes),
            )
        )
    ).scalar_one()
    assert loaded_teacher.unavailabilities == [unavailability]
    assert loaded_teacher.disputes == [dispute]

    loaded_assignment = (
        await session.execute(
            select(ScheduleAssignment)
            .where(ScheduleAssignment.id == assignment.id)
            .options(selectinload(ScheduleAssignment.disputes))
        )
    ).scalar_one()
    assert loaded_assignment.disputes == [dispute]

    # Delete em cascata: apagar a versão remove as atribuições
    await session.delete(version)
    await session.commit()
    remaining = (await session.execute(select(ScheduleAssignment))).scalars().all()
    assert remaining == []
