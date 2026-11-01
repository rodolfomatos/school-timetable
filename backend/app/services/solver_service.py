"""Serviço que envolve o solver Python existente com persistência de jobs."""

from __future__ import annotations

import logging
import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.core.config import settings
from app.models.school import (
    Course,
    Room,
    Subject,
    Class as SchoolClass,
    Teacher,
    ClassSubject,
    TeacherSubject,
)
from app.models.schedule import (
    ScheduleAssignment,
    ScheduleVersion,
    SolverJob,
    SolverJobStatus,
)
from app.models.user import User
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


def _run_solver_sync(
    job_id: str,
    institution_id: str | None,
    solver: str,
    time_limit_seconds: int,
    additional_unavailabilities: list[dict] | None,
    created_by: int | None,
    seed: int | None,
) -> None:
    """Executa o solver Python de forma síncrona (em thread separada) e persiste o job."""

    start_time = time.time()

    async def _update_job_status(
        status: str,
        **kwargs,
    ) -> None:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            job = (await db.execute(select(SolverJob).where(SolverJob.id == job_id))).scalar_one()
            job.status = status
            for key, value in kwargs.items():
                setattr(job, key, value)
            await db.commit()

    # Atualizar status para RUNNING
    import asyncio as _asyncio
    _asyncio.run(_update_job_status(SolverJobStatus.RUNNING, started_at=datetime.now(timezone.utc)))

    try:
        # Importação tardia para evitar dependência pesada no módulo principal
        from timetable.domain import (
            Disciplina,
            EntradaCurricular,
            Professor,
            Sala,
            Slot,
            Turma,
            construir_problema,
            construir_solucao_inicial,
        )
        from timetable.local_search import simulated_annealing, tabu_search
        from timetable.cp_sat_baseline import CPSATSolver

        # Buscar entidades da base de dados
        async def _fetch_entities():
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select

                courses = (await db.execute(select(Course))).scalars().all()
                rooms = (await db.execute(select(Room))).scalars().all()
                subjects = (await db.execute(select(Subject))).scalars().all()
                classes = (await db.execute(select(SchoolClass))).scalars().all()
                teachers = (await db.execute(select(Teacher))).scalars().all()
                users = (await db.execute(select(User))).scalars().all()

                # Currículo e qualificações
                class_subjects = (
                    await db.execute(
                        select(ClassSubject).where(ClassSubject.teacher_id.is_not(None))
                    )
                ).scalars().all()
                teacher_subjects = (await db.execute(select(TeacherSubject))).scalars().all()

                return (
                    courses,
                    rooms,
                    subjects,
                    classes,
                    teachers,
                    users,
                    class_subjects,
                    teacher_subjects,
                )

        (
            courses,
            rooms,
            subjects,
            classes,
            teachers,
            users,
            class_subjects,
            teacher_subjects,
        ) = _asyncio.run(_fetch_entities())

        # Construir ProblemInstance a partir dos dados do ORM
        professores_domain: dict[str, Professor] = {}
        for t in teachers:
            disponibilidade = frozenset()
            if t.availability:
                disponibilidade = frozenset(
                    Slot(dia=dia, hora=h)
                    for dia, horas in t.availability.items()
                    for h in horas
                )
            professores_domain[str(t.id)] = Professor(
                identificador=str(t.id),
                nome=t.user.full_name if t.user else f"Prof. {t.id}",
                disponibilidade=disponibilidade,
                dia_folga_preferido=t.day_off_preferred,
                prefere_manha=t.morning_preferred,
                carga_maxima_semanal=t.commute_time + 20,
                carga_minima_semanal=5,
                qualificacoes=frozenset(),
                qualificacoes_definidas=False,
            )

        # Indisponibilidades adicionais vindas da request
        unavailabilities_adicionais: dict[str, set[Slot]] = {}
        if additional_unavailabilities:
            for u in additional_unavailabilities:
                tid = str(u.get("teacher_id"))
                slot = Slot(dia=u["slot"]["dia"], hora=u["slot"]["hora"])
                unavailabilities_adicionais.setdefault(tid, set()).add(slot)

        salas_domain = {
            str(r.id): Sala(
                identificador=str(r.id),
                capacidade=r.capacity,
                tipo=r.room_type,
            )
            for r in rooms
        }
        turmas_domain = {
            str(c.id): Turma(
                identificador=str(c.id),
                ano=c.year,
                numero_alunos=c.student_count,
            )
            for c in classes
        }
        disciplinas_domain = {
            str(s.id): Disciplina(
                identificador=str(s.id),
                nome=s.name,
                carga_semanal=s.weekly_load,
                tipo_sala_requerida=s.room_type_required,
            )
            for s in subjects
        }

        # Currículo: usa ClassSubject (relação explícita)
        curriculo: list[EntradaCurricular] = []
        for cs in class_subjects:
            curriculo.append(
                EntradaCurricular(
                    turma_id=str(cs.class_id),
                    disciplina_id=str(cs.subject_id),
                    professores_elegiveis=(str(cs.teacher_id),) if cs.teacher_id else (),
                    subgrupo_id=None,  # TODO: suportar subgrupos
                )
            )

        # Qualificações: TeacherSubject
        qualificacoes: dict[str, set[str]] = {}
        for ts in teacher_subjects:
            qualificacoes.setdefault(str(ts.teacher_id), set()).add(str(ts.subject_id))
        for prof_id, prof in professores_domain.items():
            if prof_id in qualificacoes:
                professores_domain[prof_id] = prof.__class__(
                    **{
                        **prof.__dict__,
                        "qualificacoes": frozenset(qualificacoes[prof_id]),
                        "qualificacoes_definidas": True,
                    }
                )

        # Construir ProblemInstance com validação
        problema = construir_problema(
            professores=professores_domain,
            salas=salas_domain,
            turmas=turmas_domain,
            disciplinas=disciplinas_domain,
            curriculo=curriculo,
            indisponibilidades_adicionais=unavailabilities_adicionais,
        )

        if problema.tem_erros:
            # Converter diagnósticos para erro legível
            erros = [d.mensagem for d in problema.diagnosticos if d.severidade == "ERROR"]
            raise ValueError("; ".join(erros) or "ProblemInstance inválido")

        # Contexto para o solver
        ctx = problema.para_contexto()

        # Gerar slots
        slots = []
        for dia in ["segunda", "terca", "quarta", "quinta", "sexta"]:
            for hora in range(1, 9):
                slots.append(Slot(dia=dia, hora=hora))

        # Construir solução inicial viável a partir do domínio
        rng = random.Random(seed if seed is not None else 42)
        horario_inicial = construir_solucao_inicial(problema, slots, rng=rng)

        solver_params = {
            "time_limit_seconds": time_limit_seconds,
            "seed": seed if seed is not None else 42,
        }

        # Executar solver
        solver_used = solver
        resultado = None
        

        if solver == "cp_sat":
            cp_solver = CPSATSolver()
            if cp_solver.esta_disponivel():
                resultado = cp_solver.resolver(
                    horario_inicial, ctx, tempo_limite_segundos=time_limit_seconds
                )
            else:
                solver_used = "simulated_annealing"
                resultado = simulated_annealing(
                    horario_inicial,
                    ctx,
                    slots,
                    tempo_limite_segundos=time_limit_seconds,
                    semente=seed if seed is not None else 42,
                )
        elif solver == "tabu_search":
            resultado = tabu_search(
                horario_inicial,
                ctx,
                slots,
                tempo_limite_segundos=time_limit_seconds,
                semente=seed if seed is not None else 42,
            )
        else:  # simulated_annealing (default)
            resultado = simulated_annealing(
                horario_inicial,
                ctx,
                slots,
                tempo_limite_segundos=time_limit_seconds,
                semente=seed if seed is not None else 42,
            )

        # Avaliar resultado
        from timetable.objective import avaliar

        avaliacao = avaliar(resultado, ctx)

        # Verificar se o solver retornou o horário inicial (fallback de timeout sem solução)
        # Comparar se o resultado é idêntico ao inicial (mesmas aulas)
        resultado_e_inicial = (
            len(resultado.aulas) == len(horario_inicial.aulas)
            and all(
                any(
                    a2.turma == a1.turma
                    and a2.disciplina == a1.disciplina
                    and a2.professor == a1.professor
                    and a2.sala == a1.sala
                    and a2.slot == a1.slot
                    and a2.subgrupo_id == a1.subgrupo_id
                    for a2 in resultado.aulas
                )
                for a1 in horario_inicial.aulas
            )
        )

        # Determinar status final
        if avaliacao.viavel:
            final_status = SolverJobStatus.COMPLETED
        elif resultado_e_inicial and not avaliacao.viavel:
            # Timeout sem solução viável
            final_status = SolverJobStatus.TIMEOUT_NO_SOLUTION
        else:
            # Timeout com incumbent (solução viável encontrada mas tempo esgotou)
            final_status = SolverJobStatus.COMPLETED

        elapsed = time.time() - start_time

        # Persistir ScheduleVersion e Assignments se concluído com sucesso
        schedule_version_id = None
        if final_status in (SolverJobStatus.COMPLETED, SolverJobStatus.TIMEOUT_WITH_INCUMBENT) and avaliacao.viavel:
            async def _persist_schedule():
                async with AsyncSessionLocal() as db:
                    version = ScheduleVersion(
                        institution_id=institution_id,
                        status="draft",
                        solver_used=solver_used,
                        score=avaliacao.score,
                        hard_violations=len(avaliacao.violacoes_hard),
                        soft_penalties=avaliacao.penalidades_moles,
                    )
                    db.add(version)
                    await db.flush()

                    for aula in resultado.aulas:
                        assignment = ScheduleAssignment(
                            version_id=version.id,
                            class_id=int(aula.turma),
                            subject_id=int(aula.disciplina),
                            teacher_id=int(aula.professor),
                            room_id=int(aula.sala),
                            slot={"dia": aula.slot.dia, "hora": aula.slot.hora},
                        )
                        db.add(assignment)

                    await db.commit()
                    return version.id

            schedule_version_id = _asyncio.run(_persist_schedule())

        # Atualizar job com resultado final
        _asyncio.run(_update_job_status(
            final_status,
            schedule_version_id=schedule_version_id,
            score=avaliacao.score if avaliacao.viavel else None,
            hard_violations=len(avaliacao.violacoes_hard),
            soft_penalties=avaliacao.penalidades_moles,
            error=None if avaliacao.viavel else "Timeout sem solução viável" if final_status == SolverJobStatus.TIMEOUT_NO_SOLUTION else "Timeout com solução incumbent",
            elapsed_seconds=elapsed,
            seed=seed if seed is not None else 42,
            solver_params=solver_params,
            completed_at=datetime.now(timezone.utc),
        ))

    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception("Erro no solver job %s", job_id)
        _asyncio.run(_update_job_status(
            SolverJobStatus.FAILED,
            error=str(e),
            elapsed_seconds=elapsed,
            completed_at=datetime.now(timezone.utc),
        ))


def create_solver_job(
    institution_id: str | None,
    solver: str,
    time_limit_seconds: int,
    additional_unavailabilities: list[dict] | None = None,
    created_by: int | None = None,
    seed: int | None = None,
) -> str:
    """Cria um job de solver persistente e devolve o ID do job."""

    job_id = str(uuid.uuid4())

    async def _create_job():
        async with AsyncSessionLocal() as db:
            job = SolverJob(
                id=job_id,
                institution_id=institution_id,
                status=SolverJobStatus.PENDING,
                solver=solver,
                time_limit_seconds=time_limit_seconds,
                additional_unavailabilities=additional_unavailabilities,
                created_by=created_by,
                seed=seed if seed is not None else 42,
            )
            db.add(job)
            await db.commit()

    import asyncio as _asyncio
    _asyncio.run(_create_job())

    # Executar em thread separada para não bloquear a API
    executor = ThreadPoolExecutor(max_workers=settings.SOLVER_MAX_WORKERS)
    executor.submit(
        _run_solver_sync,
        job_id,
        institution_id,
        solver,
        time_limit_seconds,
        additional_unavailabilities,
        created_by,
        seed,
    )

    return job_id


async def get_solver_job(job_id: str) -> SolverJob | None:
    """Devolve o job de solver por ID."""

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        return (await db.execute(select(SolverJob).where(SolverJob.id == job_id))).scalar_one_or_none()


async def list_solver_jobs(
    institution_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[SolverJob]:
    """Lista jobs de solver com filtros opcionais."""

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        query = select(SolverJob).order_by(SolverJob.created_at.desc())
        if institution_id:
            query = query.where(SolverJob.institution_id == institution_id)
        if status:
            query = query.where(SolverJob.status == status)
        query = query.limit(limit).offset(offset)
        return (await db.execute(query)).scalars().all()


async def cancel_solver_job(job_id: str, cancelled_by: int | None = None) -> bool:
    """Cancela um job pendente ou em execução."""

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        job = (await db.execute(select(SolverJob).where(SolverJob.id == job_id))).scalar_one_or_none()
        if not job:
            return False
        if job.status not in (SolverJobStatus.PENDING, SolverJobStatus.RUNNING):
            return False
        job.status = SolverJobStatus.CANCELLED
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        return True