"""Router de indisponibilidades docentes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.schedule import Unavailability
from app.models.school import Teacher
from app.models.user import Role, User
from app.schemas.schedule import UnavailabilityCreate, UnavailabilityRead

router = APIRouter(prefix="/unavailability", tags=["unavailability"])

_ALLOWED_ROLES = (Role.TEACHER, Role.ADMIN, Role.COORDINATOR)


async def _teacher_profile(db: AsyncSession, user: User) -> Teacher:
    """Devolve o perfil de docente do utilizador autenticado."""

    result = await db.execute(select(Teacher).where(Teacher.user_id == user.id))
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O utilizador não tem perfil de docente",
        )
    return teacher


@router.get("", response_model=list[UnavailabilityRead])
async def list_unavailabilities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista indisponibilidades: docentes vêem as suas; admin/coordenação vêem as da instituição."""

    if current_user.role not in _ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )

    stmt = select(Unavailability)
    if current_user.role == Role.TEACHER:
        teacher = await _teacher_profile(db, current_user)
        stmt = stmt.where(Unavailability.teacher_id == teacher.id)
    elif current_user.institution_id:
        stmt = stmt.join(Teacher).where(
            Teacher.institution_id == current_user.institution_id
        )

    result = await db.execute(stmt.order_by(Unavailability.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=UnavailabilityRead, status_code=status.HTTP_201_CREATED)
async def create_unavailability(
    payload: UnavailabilityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria (ou actualiza) a indisponibilidade de um docente num slot."""

    if current_user.role not in _ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
        )

    if current_user.role == Role.TEACHER:
        # Um docente só pode declarar indisponibilidade para si próprio.
        teacher = await _teacher_profile(db, current_user)
        teacher_id = teacher.id
    else:
        if payload.teacher_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="teacher_id é obrigatório para admin/coordenação",
            )
        teacher = (
            await db.execute(select(Teacher).where(Teacher.id == payload.teacher_id))
        ).scalar_one_or_none()
        if teacher is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Docente não encontrado",
            )
        teacher_id = teacher.id

    # Comparar JSON usando cast para JSONB (PostgreSQL)
    existing = (
        await db.execute(
            select(Unavailability).where(
                Unavailability.teacher_id == teacher_id,
                cast(Unavailability.slot, JSONB) == cast(payload.slot, JSONB),
            )
        )
    ).scalar_one_or_none()

    if existing is not None:
        existing.justification = payload.justification
        existing.reason = payload.reason
        existing.updated_by = current_user.id
        await db.commit()
        await db.refresh(existing)
        return existing

    unavailability = Unavailability(
        teacher_id=teacher_id,
        slot=payload.slot,
        justification=payload.justification,
        reason=payload.reason,
        created_by=current_user.id,
    )
    db.add(unavailability)
    await db.commit()
    await db.refresh(unavailability)
    return unavailability
