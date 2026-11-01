"""Serviço que envolve o solver Python existente."""

from __future__ import annotations

import logging
import random
import uuid
from concurrent.futures import ThreadPoolExecutor

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
from app.models.user import User
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Armazenamento em memória de tarefas (em produção, usar Redis/DB)
_solver_tasks: dict[str, dict] = {}


def _run_solver_sync(
    task_id: str,
    institution_id: str | None,
    solver: str,
    time_limit_seconds: int,
    additional_unavailabilities: list[dict] | None,
) -> None:
    """Executa o solver Python de forma síncrona (em thread separada)."""

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
        # Nota: esta função corre numa thread, então precisamos de uma nova sessão
        import asyncio as _asyncio

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
        horario_inicial = construir_solucao_inicial(problema, slots, rng=random.Random(42))

        # Executar solver
        if solver == "cp_sat":
            cp_solver = CPSATSolver()
            if cp_solver.esta_disponivel():
                resultado = cp_solver.resolver(
                    horario_inicial, ctx, tempo_limite_segundos=time_limit_seconds
                )
            else:
                # Fallback para simulated annealing
                resultado = simulated_annealing(
                    horario_inicial,
                    ctx,
                    slots,
                    tempo_limite_segundos=time_limit_seconds,
                    semente=42,
                )
        elif solver == "tabu_search":
            resultado = tabu_search(
                horario_inicial,
                ctx,
                slots,
                tempo_limite_segundos=time_limit_seconds,
                semente=42,
            )
        else:  # simulated_annealing (default)
            resultado = simulated_annealing(
                horario_inicial,
                ctx,
                slots,
                tempo_limite_segundos=time_limit_seconds,
                semente=42,
            )

        # Avaliar resultado
        from timetable.objective import avaliar

        avaliacao = avaliar(resultado, ctx)

        # Guardar resultado na tarefa
        _solver_tasks[task_id] = {
            "status": "completed",
            "schedule_version_id": None,  # Será preenchido quando guardar na BD
            "score": avaliacao.score,
            "hard_violations": len(avaliacao.violacoes_hard),
            "soft_penalties": avaliacao.penalidades_moles,
            "error": None,
            "result": resultado,
            "avaliacao": avaliacao,
            "ctx": ctx,
        }

    except Exception as e:
        logger.exception("Erro no solver")
        _solver_tasks[task_id] = {
            "status": "failed",
            "schedule_version_id": None,
            "score": None,
            "hard_violations": None,
            "soft_penalties": None,
            "error": str(e),
        }


def create_solver_task(
    institution_id: str | None,
    solver: str,
    time_limit_seconds: int,
    additional_unavailabilities: list[dict] | None = None,
) -> str:
    """Cria uma tarefa de solver e devolve o ID da tarefa."""

    task_id = str(uuid.uuid4())
    _solver_tasks[task_id] = {
        "status": "pending",
        "schedule_version_id": None,
        "score": None,
        "hard_violations": None,
        "soft_penalties": None,
        "error": None,
    }

    # Executar em thread separada para não bloquear a API
    executor = ThreadPoolExecutor(max_workers=settings.SOLVER_MAX_WORKERS)
    executor.submit(
        _run_solver_sync,
        task_id,
        institution_id,
        solver,
        time_limit_seconds,
        additional_unavailabilities,
    )

    return task_id


def get_solver_task(task_id: str) -> dict | None:
    """Devolve o estado de uma tarefa de solver."""

    return _solver_tasks.get(task_id)