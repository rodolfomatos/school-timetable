"""Router de horários: execução do solver, listagem de versões."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_role
from app.core.limiter import limiter
from app.models.user import User, Role
from app.models.schedule import ScheduleVersion, ScheduleAssignment
from app.services.solver_service import create_solver_task, get_solver_task
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
    _: User = Depends(require_role(Role.ADMIN, Role.COORDINATOR)),
):
    """Executa o solver de horário de forma assíncrona (rate limited: 5/min)."""

    task_id = create_solver_task(
        institution_id=solver_request.institution_id,
        solver=solver_request.solver,
        time_limit_seconds=solver_request.time_limit_seconds,
        additional_unavailabilities=solver_request.additional_unavailabilities,
    )

    return SolverRunResponse(
        task_id=task_id,
        status="pending",
        message="Solver iniciado. Consulte /scheduler/status/{task_id} para o resultado.",
    )


@router.get("/status/{task_id}", response_model=SolverStatusResponse)
async def solver_status(
    task_id: str,
    _: User = Depends(get_current_user),
):
    """Devolve o estado de uma tarefa de solver."""

    task = get_solver_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )

    return SolverStatusResponse(
        task_id=task_id,
        status=task["status"],
        schedule_version_id=task["schedule_version_id"],
        score=task["score"],
        hard_violations=task["hard_violations"],
        soft_penalties=task["soft_penalties"],
        error=task["error"],
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
