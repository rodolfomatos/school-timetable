"""Cria contas e dados de domínio de demonstração.

Idempotente: contas e entidades existentes são actualizadas apenas quando
lhes falta a instituição demo.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal, engine
from app.models.school import (
    Class as SchoolClass,
    ClassSubject,
    Course,
    Room,
    Subject,
    Teacher,
)
from app.models.user import Role, User

from scripts.create_user import create_user

DEMO_PASSWORD = "senha123"
DEMO_INSTITUTION = "demo"

DEMO_USERS = (
    ("admin@escola.pt", Role.ADMIN, "Administrador Demo"),
    ("professor@escola.pt", Role.TEACHER, "Professor Demo"),
    ("professor2@escola.pt", Role.TEACHER, "Professor Demo 2"),
    ("aluno@escola.pt", Role.STUDENT, "Aluno Demo"),
)

ROOMS = (
    ("Sala Demo 1", 30),
    ("Sala Demo 2", 30),
)

SUBJECTS = (
    ("MAT", "Matemática", 3),
    ("POR", "Português", 3),
    ("FIS", "Física", 2),
)

CLASSES = (
    ("Demo 1ºA", 24),
    ("Demo 1ºB", 22),
)


async def _get_or_create(
    db,
    model,
    defaults: dict | None = None,
    *,
    institution_id: str | None = None,
    **filters,
):
    existing = (
        await db.execute(select(model).filter_by(**filters))
    ).scalar_one_or_none()
    if existing is not None:
        if institution_id and getattr(existing, "institution_id", None) is None:
            existing.institution_id = institution_id
        return existing, False
    obj = model(**filters, **(defaults or {}))
    if institution_id and hasattr(obj, "institution_id"):
        obj.institution_id = institution_id
    db.add(obj)
    await db.flush()
    return obj, True


async def _ensure_demo_institution() -> None:
    """Garante que contas demo e perfis docentes pertencem à instituição demo."""

    emails = [email for email, _, _ in DEMO_USERS]
    async with AsyncSessionLocal() as db:
        users = (
            await db.execute(select(User).where(User.email.in_(emails)))
        ).scalars().all()
        for user in users:
            if user.institution_id is None:
                user.institution_id = DEMO_INSTITUTION

        teachers = (
            await db.execute(
                select(Teacher).where(Teacher.user_id.in_([u.id for u in users]))
            )
        ).scalars().all()
        for teacher in teachers:
            if teacher.institution_id is None:
                teacher.institution_id = DEMO_INSTITUTION

        await db.commit()


async def seed_domain() -> None:
    """Cria um conjunto mínimo e viável para o solver gerar horário."""

    async with AsyncSessionLocal() as db:
        course, course_created = await _get_or_create(
            db,
            Course,
            {"name": "Curso Demo"},
            institution_id=DEMO_INSTITUTION,
            code="DEMO",
        )

        for name, capacity in ROOMS:
            await _get_or_create(
                db,
                Room,
                {"capacity": capacity, "room_type": "normal"},
                institution_id=DEMO_INSTITUTION,
                name=name,
            )

        subjects: list[Subject] = []
        for code, name, weekly_load in SUBJECTS:
            subject, _ = await _get_or_create(
                db,
                Subject,
                {
                    "name": name,
                    "weekly_load": weekly_load,
                    "room_type_required": "normal",
                    "course_id": course.id,
                },
                institution_id=DEMO_INSTITUTION,
                code=code,
            )
            subjects.append(subject)

        classes: list[SchoolClass] = []
        for name, student_count in CLASSES:
            school_class, _ = await _get_or_create(
                db,
                SchoolClass,
                {
                    "course_id": course.id,
                    "year": 1,
                    "student_count": student_count,
                },
                institution_id=DEMO_INSTITUTION,
                name=name,
            )
            classes.append(school_class)

        teachers = (
            await db.execute(
                select(Teacher)
                .join(User, User.id == Teacher.user_id)
                .where(
                    User.email.in_(
                        ["professor@escola.pt", "professor2@escola.pt"]
                    )
                )
                .order_by(User.email)
            )
        ).scalars().all()
        if len(teachers) < 2:
            raise RuntimeError(
                "Perfis de docente demo não encontrados "
                "(professor@escola.pt / professor2@escola.pt)"
            )

        # Distribui as turmas pelos docentes para não exceder a carga máxima.
        for index, school_class in enumerate(classes):
            teacher = teachers[index % len(teachers)]
            for subject in subjects:
                link, _ = await _get_or_create(
                    db,
                    ClassSubject,
                    {"teacher_id": teacher.id},
                    institution_id=DEMO_INSTITUTION,
                    class_id=school_class.id,
                    subject_id=subject.id,
                )
                if link.teacher_id != teacher.id:
                    link.teacher_id = teacher.id

        await db.commit()

    if course_created:
        print("+ domínio demo criado (curso, salas, disciplinas, turmas)")
    else:
        print("= domínio demo já existia, completado/actualizado")


async def main() -> None:
    try:
        for email, role, name in DEMO_USERS:
            await create_user(
                email=email,
                password=DEMO_PASSWORD,
                role=role,
                full_name=name,
                institution_id=DEMO_INSTITUTION,
                skip_existing=True,
            )
        await _ensure_demo_institution()
        await seed_domain()
    finally:
        await engine.dispose()
    print(f"Contas demo prontas (palavra-passe: {DEMO_PASSWORD})")


if __name__ == "__main__":
    asyncio.run(main())
