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


@router.post("/run", response_model=SolverRunResponse)
@limiter.limit("5/minute")
async def run_solver(
    request: Request,
    solver_request: SolverRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN, Role.COORDINATOR)),
):
    """Executa o solver de horário de forma assíncrona (rate limited: 5/min)."""

    job_id = await create_solver_job(
        institution_id=solver_request.institution_id,
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
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
):
    """Lista jobs de solver com filtros opcionais."""

    jobs = await list_solver_jobs(
        institution_id=None,  # TODO: filtrar por institution_id do utilizador
        status=status,
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
    """Cancela um job pendente ou em execução."""

    success = await cancel_solver_job(job_id, cancelled_by=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job não encontrado ou não pode ser cancelado",
        )


@router.get("/versions", response_model=list[ScheduleVersionRead])
async def list_versions(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista versões de horário."""

    result = await db.execute(select(ScheduleVersion))
    return result.scalars().all()


@router.get("/versions/{version_id}/assignments", response_model=list[ScheduleAssignmentRead])
async def get_assignments(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista atribuições de uma versão de horário."""

    result = await db.execute(
        select(ScheduleAssignment).where(ScheduleAssignment.version_id == version_id)
    )
    return result.scalars().all()
