"""Router de contestações: criar, listar, aceitar/rejeitar."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.deps import get_db, get_current_user, require_role
from app.models.user import User, Role
from app.models.schedule import Dispute, ScheduleAssignment, ScheduleVersion
from app.models.school import Teacher
from app.schemas.schedule import DisputeCreate, DisputeRead, DisputeUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/disputes", tags=["disputes"])


def _get_institution_id(current_user: User) -> str | None:
    """Extrai institution_id do utilizador atual."""
    return current_user.institution_id


@router.post("/", response_model=DisputeRead, status_code=status.HTTP_201_CREATED)
async def create_dispute(
    dispute_in: DisputeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submete uma contestação (apenas docentes)."""

    # Verificar que o utilizador é o docente da aula
    result = await db.execute(
        select(ScheduleAssignment).where(
            ScheduleAssignment.id == dispute_in.assignment_id
        )
    )
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aula não encontrada",
        )

    # Obter o perfil de professor do utilizador
    result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas docentes podem submeter contestações",
        )

    if assignment.teacher_id != teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não pode contestar uma aula que não lhe está atribuída",
        )

    # Verificar se já existe uma contestação para esta atribuição por este docente
    result = await db.execute(
        select(Dispute).where(
            Dispute.assignment_id == dispute_in.assignment_id,
            Dispute.teacher_id == teacher.id,
            Dispute.status == "pending",
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma contestação pendente para esta aula",
        )

    dispute = Dispute(
        teacher_id=teacher.id,
        assignment_id=dispute_in.assignment_id,
        reason=dispute_in.reason,
        justification=dispute_in.justification,
        status="pending",
    )
    db.add(dispute)
    await db.commit()
    await db.refresh(dispute)
    return dispute


@router.get("/", response_model=list[DisputeRead])
async def list_disputes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista contestações (docente vê as suas, admin vê da sua instituição)."""

    # Obter o professor do utilizador se for docente
    result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = result.scalar_one_or_none()

    institution_id = current_user.institution_id
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    if current_user.role == Role.ADMIN:
        # Admin vê contestações da sua instituição
        result = await db.execute(
            select(Dispute)
            .join(ScheduleAssignment, Dispute.assignment_id == ScheduleAssignment.id)
            .join(ScheduleVersion, ScheduleAssignment.version_id == ScheduleVersion.id)
            .where(ScheduleVersion.institution_id == institution_id)
        )
    elif teacher is not None:
        result = await db.execute(
            select(Dispute).where(Dispute.teacher_id == teacher.id)
        )
    else:
        result = await db.execute(select(Dispute).where(Dispute.id == -1))  # vazio

    return result.scalars().all()


@router.patch("/{dispute_id}", response_model=DisputeRead)
async def update_dispute(
    dispute_id: int,
    dispute_in: DisputeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """Aceita ou rejeita uma contestação (apenas admin da mesma instituição)."""

    institution_id = current_user.institution_id
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    result = await db.execute(
        select(Dispute)
        .join(ScheduleAssignment, Dispute.assignment_id == ScheduleAssignment.id)
        .join(ScheduleVersion, ScheduleAssignment.version_id == ScheduleVersion.id)
        .where(Dispute.id == dispute_id, ScheduleVersion.institution_id == institution_id)
    )
    dispute = result.scalar_one_or_none()
    if dispute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contestação não encontrada ou acesso negado",
        )

    if dispute.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contestação já foi resolvida",
        )

    dispute.status = dispute_in.status
    dispute.resolved_at = datetime.now(timezone.utc)
    dispute.resolved_by = current_user.id
    logger.info(
        "contestação resolvida id=%s status=%s resolved_by=%s",
        dispute.id,
        dispute.status,
        current_user.id,
    )

    await db.commit()
    await db.refresh(dispute)

    # Se aceito, criar indisponibilidade automática e reexecutar solver
    if dispute_in.status == "accepted":
        from app.models.schedule import Unavailability

        # Obter o slot da atribuição contestada
        result = await db.execute(
            select(ScheduleAssignment).where(
                ScheduleAssignment.id == dispute.assignment_id
            )
        )
        assignment = result.scalar_one_or_none()
        if assignment:
            # Criar indisponibilidade para o professor nesse slot
            unavailability = Unavailability(
                teacher_id=dispute.teacher_id,
                slot=assignment.slot,
                justification=dispute.justification,
                reason=f"Contestação aceita: {dispute.reason}",
            )
            db.add(unavailability)
            await db.commit()

            # TODO: Disparar reexecução do solver (assíncrono)
            # Isso seria feito via task queue (Celery/RQ) ou endpoint separado

    return dispute