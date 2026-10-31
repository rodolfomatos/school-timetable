"""Router de disciplinas: CRUD completo."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_role
from app.models.school import Subject
from app.models.user import Role, User
from app.schemas.school import SubjectCreate, SubjectRead, SubjectUpdate

router = APIRouter(prefix="/schools/subjects", tags=["schools"])


@router.post("/", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_in: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN, Role.COORDINATOR)),
):
    """Cria uma nova disciplina."""

    subject = Subject(**subject_in.model_dump())
    db.add(subject)
    await db.commit()
    await db.refresh(subject)
    return subject


@router.get("/", response_model=list[SubjectRead])
async def list_subjects(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista todas as disciplinas."""

    result = await db.execute(select(Subject))
    return result.scalars().all()


@router.get("/{subject_id}", response_model=SubjectRead)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Obtém uma disciplina pelo ID."""

    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada",
        )
    return subject


@router.put("/{subject_id}", response_model=SubjectRead)
async def update_subject(
    subject_id: int,
    subject_in: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN, Role.COORDINATOR)),
):
    """Atualiza uma disciplina."""

    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada",
        )

    update_data = subject_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)

    await db.commit()
    await db.refresh(subject)
    return subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
):
    """Remove uma disciplina."""

    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada",
        )

    await db.delete(subject)
    await db.commit()
