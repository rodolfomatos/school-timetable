"""Testes de autenticação, privilégios e hardening de cookies (T050)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models.schedule import Dispute, ScheduleAssignment, ScheduleVersion
from app.models.school import Class, Course, Room, Subject, Teacher
from app.models.user import Role, User


@pytest.fixture
async def api() -> AsyncIterator[tuple[AsyncClient, async_sessionmaker[AsyncSession]]]:
    """Cliente HTTP sobre a app real, com SQLite partilhado em memória."""

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, factory

    app.dependency_overrides.clear()
    await engine.dispose()


async def _create_user(
    factory: async_sessionmaker[AsyncSession],
    email: str,
    role: str,
    password: str = "segredo123",
) -> User:
    async with factory() as session:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name="Utilizador Sintético",
            role=role,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.mark.parametrize("requested_role", [Role.ADMIN, Role.COORDINATOR, Role.TEACHER])
async def test_public_registration_always_forces_student(
    api: tuple[AsyncClient, async_sessionmaker[AsyncSession]],
    requested_role: str,
) -> None:
    """Papéis elevados pedidos no registo público são ignorados."""

    client, factory = api
    email = f"registo-{requested_role}@example.com"

    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "segredo123",
            "full_name": "Tentativa de Escalada",
            "role": requested_role,
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == Role.STUDENT

    async with factory() as session:
        stored = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
        assert stored.role == Role.STUDENT


async def test_login_sets_httponly_cookies_and_refresh_works(
    api: tuple[AsyncClient, async_sessionmaker[AsyncSession]],
) -> None:
    """O login define access+refresh httpOnly; o refresh renova o acesso."""

    client, factory = api
    await _create_user(factory, "cookie@example.com", Role.STUDENT)

    response = await client.post(
        "/auth/login",
        json={"email": "cookie@example.com", "password": "segredo123"},
    )
    assert response.status_code == 200

    cookies = response.headers.get_list("set-cookie")
    assert any(c.startswith("access_token=") and "HttpOnly" in c for c in cookies)
    assert any(c.startswith("refresh_token=") and "HttpOnly" in c for c in cookies)

    refreshed = await client.post("/auth/refresh")
    assert refreshed.status_code == 200
    assert any(
        c.startswith("access_token=") for c in refreshed.headers.get_list("set-cookie")
    )


async def test_cookie_secure_flag_follows_environment(
    api: tuple[AsyncClient, async_sessionmaker[AsyncSession]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Secure só é exigido em produção; em local continua testável."""

    client, factory = api
    await _create_user(factory, "ambiente@example.com", Role.STUDENT)

    dev = await client.post(
        "/auth/login",
        json={"email": "ambiente@example.com", "password": "segredo123"},
    )
    assert not any("Secure" in c for c in dev.headers.get_list("set-cookie"))

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    prod = await client.post(
        "/auth/login",
        json={"email": "ambiente@example.com", "password": "segredo123"},
    )
    assert any("Secure" in c for c in prod.headers.get_list("set-cookie"))


async def test_only_admin_can_change_roles(
    api: tuple[AsyncClient, async_sessionmaker[AsyncSession]],
) -> None:
    """Escalada horizontal: um utilizador comum não altera papéis."""

    client, factory = api
    admin = await _create_user(factory, "admin@example.com", Role.ADMIN)
    student = await _create_user(factory, "aluno@example.com", Role.STUDENT)

    # Sem autenticação
    anonymous = await client.patch(f"/users/{student.id}", json={"role": Role.ADMIN})
    assert anonymous.status_code == 401

    # Autenticado como student
    await client.post(
        "/auth/login",
        json={"email": "aluno@example.com", "password": "segredo123"},
    )
    forbidden = await client.patch(f"/users/{student.id}", json={"role": Role.ADMIN})
    assert forbidden.status_code == 403

    async with factory() as session:
        unchanged = (
            await session.execute(select(User).where(User.id == student.id))
        ).scalar_one()
        assert unchanged.role == Role.STUDENT

    # Admin autorizado
    await client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "segredo123"},
    )
    allowed = await client.patch(
        f"/users/{student.id}", json={"role": Role.COORDINATOR}
    )
    assert allowed.status_code == 200
    assert allowed.json()["role"] == Role.COORDINATOR
    assert allowed.json()["id"] == student.id
    assert admin.role == Role.ADMIN


async def _seed_dispute(
    factory: async_sessionmaker[AsyncSession],
    teacher_user_id: int,
) -> tuple[Dispute, User]:
    """Cria um horário mínimo com uma contestação pendente."""

    async with factory() as session:
        course = Course(code="MED", name="Medicina")
        room = Room(name="Sala M1", capacity=20, course=course)
        subject = Subject(code="BIO", name="Biologia", weekly_load=2, course=course)
        school_class = Class(name="Turma M1", year=1, student_count=20, course=course)
        teacher = Teacher(user_id=teacher_user_id, employee_code="DOC-MED")
        version = ScheduleVersion(status="published")
        session.add_all([course, room, subject, school_class, teacher, version])
        await session.flush()

        assignment = ScheduleAssignment(
            version=version,
            class_=school_class,
            subject=subject,
            teacher=teacher,
            room=room,
            slot={"dia": "segunda", "hora": 1},
        )
        session.add(assignment)
        await session.flush()

        dispute = Dispute(
            teacher=teacher,
            assignment=assignment,
            reason="Conflito sintético",
            justification="deslocamento",
        )
        session.add(dispute)
        await session.commit()
        await session.refresh(dispute)
        return dispute, teacher


async def test_dispute_resolution_records_authenticated_admin(
    api: tuple[AsyncClient, async_sessionmaker[AsyncSession]],
) -> None:
    """resolved_by usa o ID do admin autenticado, nunca um valor hard-coded."""

    client, factory = api
    teacher_user = await _create_user(factory, "docente@example.com", Role.TEACHER)
    admin = await _create_user(factory, "admin2@example.com", Role.ADMIN)
    dispute, _ = await _seed_dispute(factory, teacher_user.id)
    assert admin.id != 1, "o teste exige que o admin não seja o ID hard-coded 1"

    # Docente não pode resolver a própria contestação (escalada vertical)
    await client.post(
        "/auth/login",
        json={"email": "docente@example.com", "password": "segredo123"},
    )
    forbidden = await client.patch(
        f"/disputes/{dispute.id}", json={"status": "accepted"}
    )
    assert forbidden.status_code == 403

    # Admin resolve; resolved_by tem de ser o admin autenticado
    await client.post(
        "/auth/login",
        json={"email": "admin2@example.com", "password": "segredo123"},
    )
    response = await client.patch(
        f"/disputes/{dispute.id}", json={"status": "accepted"}
    )
    assert response.status_code == 200
    assert response.json()["resolved_by"] == admin.id
