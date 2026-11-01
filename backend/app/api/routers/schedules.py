"""Router de horários: execução do solver, listagem de versões."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_role
from app.core.limiter import limiter
from app.models.user import User, Role
from app.models.schedule import ScheduleVersion, ScheduleAssignment
from app.services.solver_service import (
    create_solver_job,
    get_solver_job,
    list_solver_jobs,
    cancel_solver_job,
)
from app.schemas.schedule import (
    SolverRunRequest,
    SolverRunResponse,
    SolverStatusResponse,
    ScheduleVersionRead,
    ScheduleAssignmentRead,
)

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


def _get_institution_id(current_user: User) -> str | None:
    """Extrai institution_id do utilizador atual."""
    return current_user.institution_id


@router.post("/run", response_model=SolverRunResponse)
@limiter.limit("5/minute")
async def run_solver(
    request: Request,
    solver_request: SolverRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN, Role.COORDINATOR)),
):
    """Executa o solver de horário de forma assíncrona (rate limited: 5/min)."""

    institution_id = solver_request.institution_id or _get_institution_id(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="institution_id é obrigatório (no pedido ou no utilizador)",
        )

    job_id = await create_solver_job(
        institution_id=institution_id,
        solver=solver_request.solver,
        time_limit_seconds=solver_request.time_limit_seconds,
        additional_unavailabilities=solver_request.additional_unavailabilities,
        created_by=current_user.id,
    )

    return SolverRunResponse(
        task_id=job_id,
        status="pending",
        message="Solver iniciado. Consulte /scheduler/status/{task_id} para o resultado.",
    )


@router.get("/status/{job_id}", response_model=SolverStatusResponse)
async def solver_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Devolve o estado de um job de solver."""

    job = await get_solver_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job não encontrado",
        )

    # Verificar isolamento institucional
    user_inst = _get_institution_id(current_user)
    if user_inst and job.institution_id != user_inst:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: job pertence a outra instituição",
        )

    return SolverStatusResponse(
        task_id=job.id,
        status=job.status,
        schedule_version_id=job.schedule_version_id,
        score=job.score,
        hard_violations=job.hard_violations,
        soft_penalties=job.soft_penalties,
        error=job.error,
    )


@router.get("/jobs", response_model=list[SolverStatusResponse])
async def list_jobs(
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
):
    """Lista jobs de solver com filtros opcionais e isolamento institucional."""

    institution_id = _get_institution_id(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    jobs = await list_solver_jobs(
        institution_id=institution_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [
        SolverStatusResponse(
            task_id=job.id,
            status=job.status,
            schedule_version_id=job.schedule_version_id,
            score=job.score,
            hard_violations=job.hard_violations,
            soft_penalties=job.soft_penalties,
            error=job.error,
        )
        for job in jobs
    ]


@router.post("/jobs/{job_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(
    job_id: str,
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """Cancela um job pendente ou em execução (apenas admin da mesma instituição)."""

    job = await get_solver_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job não encontrado",
        )

    user_inst = _get_institution_id(current_user)
    if user_inst and job.institution_id != user_inst:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: job pertence a outra instituição",
        )

    success = await cancel_solver_job(job_id, cancelled_by=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job não encontrado ou não pode ser cancelado",
        )


@router.get("/versions", response_model=list[ScheduleVersionRead])
async def list_versions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista versões de horário da instituição do utilizador."""

    institution_id = _get_institution_id(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    result = await db.execute(
        select(ScheduleVersion).where(ScheduleVersion.institution_id == institution_id)
    )
    return result.scalars().all()


@router.get("/versions/{version_id}/assignments", response_model=list[ScheduleAssignmentRead])
async def get_assignments(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista atribuições de uma versão de horário (com verificação de instituição)."""

    institution_id = _get_institution_id(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    # Verificar que a versão pertence à instituição
    version_result = await db.execute(
        select(ScheduleVersion).where(
            ScheduleVersion.id == version_id,
            ScheduleVersion.institution_id == institution_id,
        )
    )
    version = version_result.scalar_one_or_none()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Versão não encontrada ou acesso negado",
        )

    result = await db.execute(
        select(ScheduleAssignment).where(ScheduleAssignment.version_id == version_id)
    )
    return result.scalars().all()