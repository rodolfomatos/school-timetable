"""Testes de regressão T054: semântica dos subgrupos."""

from __future__ import annotations

import pytest

from timetable.domain import (
    EntradaCurricular,
    construir_problema,
)
from timetable.seed import construir_solucao_inicial
from timetable.models import Aula, Horario, Professor, Sala, Slot, Subgrupo, Turma, Disciplina


def _prof(id_: str, disp: list[Slot] | None = None) -> Professor:
    return Professor(
        identificador=id_,
        nome=f"Prof {id_}",
        disponibilidade=frozenset(disp) if disp else frozenset(),
        qualificacoes={"D1"},
        qualificacoes_definidas=True,
    )


def _sala(id_: str, cap: int = 30) -> Sala:
    return Sala(identificador=id_, capacidade=cap, tipo="normal")


def _turma(id_: str, alunos: int = 20) -> Turma:
    return Turma(identificador=id_, ano=1, numero_alunos=alunos)


def _disc(id_: str, carga: int = 2) -> Disciplina:
    return Disciplina(identificador=id_, nome=f"Disc {id_}", carga_semanal=carga, tipo_sala_requerida="normal")


def test_h03_turma_inteira_bloqueia_subgrupo() -> None:
    """Turma inteira (subgrupo_id=None) bloqueia subgrupo no mesmo slot."""

    slots = [Slot("segunda", h) for h in range(8, 18)]
    profs = {"P1": _prof("P1", slots)}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1", alunos=30)}
    disciplinas = {"D1": _disc("D1", carga=2)}
    subgrupos = {"SG1": Subgrupo(identificador="SG1", turma_pai="T1", nome="Grupo A", numero_alunos=15)}

    curriculo = [
        EntradaCurricular("T1", "D1", professores_elegiveis=("P1",)),  # turma inteira
        EntradaCurricular("T1", "D1", professores_elegiveis=("P1",), subgrupo_id="SG1"),  # subgrupo
    ]

    problema = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
        subgrupos=subgrupos,
    )

    # Construir solução inicial
    horario = construir_solucao_inicial(problema, slots, rng=None)

    # Verificar H03: turma inteira e subgrupo não podem sobrepor-se
    from timetable.constraints import verificar_hard

    ctx = problema.para_contexto()
    violacoes = verificar_hard(horario, ctx)
    h03_violacoes = [v for v in violacoes if v.startswith("H03:")]
    assert h03_violacoes == [], f"H03 violado: {h03_violacoes}"


def test_h03_subgrupos_diferentes_podem_paralelo() -> None:
    """Subgrupos diferentes da mesma turma podem decorrer em paralelo."""

    slots = [Slot("segunda", h) for h in range(8, 18)]
    profs = {
        "P1": _prof("P1", slots),
        "P2": _prof("P2", slots),
    }
    salas = {"S1": _sala("S1"), "S2": _sala("S2")}
    turmas = {"T1": _turma("T1", alunos=30)}
    disciplinas = {"D1": _disc("D1", carga=1)}
    subgrupos = {
        "SG1": Subgrupo(identificador="SG1", turma_pai="T1", nome="Grupo A", numero_alunos=15),
        "SG2": Subgrupo(identificador="SG2", turma_pai="T1", nome="Grupo B", numero_alunos=15),
    }

    curriculo = [
        EntradaCurricular("T1", "D1", professores_elegiveis=("P1",), subgrupo_id="SG1"),
        EntradaCurricular("T1", "D1", professores_elegiveis=("P2",), subgrupo_id="SG2"),
    ]

    problema = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
        subgrupos=subgrupos,
    )

    slots = [Slot("segunda", h) for h in range(8, 18)]
    horario = construir_solucao_inicial(problema, slots, rng=None)

    from timetable.constraints import verificar_hard

    ctx = problema.para_contexto()
    violacoes = verificar_hard(horario, ctx)
    h03_violacoes = [v for v in violacoes if v.startswith("H03:")]
    assert h03_violacoes == [], f"H03 violado indevidamente: {h03_violacoes}"
    # Deve ter 2 aulas (uma por subgrupo)
    assert len(horario.aulas) == 2
    assert {a.subgrupo_id for a in horario.aulas} == {"SG1", "SG2"}


def test_local_search_preserva_subgrupo_id() -> None:
    """Operadores de movimento preservam subgrupo_id."""

    slots = [Slot("segunda", h) for h in range(8, 18)]
    profs = {"P1": _prof("P1", slots)}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1", alunos=20)}
    disciplinas = {"D1": _disc("D1", carga=2)}
    subgrupos = {"SG1": Subgrupo(identificador="SG1", turma_pai="T1", nome="Grupo A", numero_alunos=10)}

    curriculo = [
        EntradaCurricular("T1", "D1", professores_elegiveis=("P1",), subgrupo_id="SG1"),
    ]

    problema = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
        subgrupos=subgrupos,
    )

    horario = construir_solucao_inicial(problema, slots, rng=None)

    # Todas as aulas devem ter subgrupo_id="SG1"
    assert all(a.subgrupo_id == "SG1" for a in horario.aulas)

    # Aplicar operador de exchange
    from timetable.local_search import _gerar_vizinho_exchange
    import random

    rng = random.Random(42)
    vizinho, _ = _gerar_vizinho_exchange(horario, slots, rng)

    if vizinho is not None:
        assert all(a.subgrupo_id == "SG1" for a in vizinho.aulas)

    # Aplicar operador de modify
    from timetable.local_search import _gerar_vizinho_modify

    vizinho2, _ = _gerar_vizinho_modify(horario, slots, rng)

    if vizinho2 is not None:
        assert all(a.subgrupo_id == "SG1" for a in vizinho2.aulas)


def test_cpsat_h03_subgrupo() -> None:
    """CP-SAT respeita H03 com subgrupos (integração rápida)."""

    from timetable.cp_sat_baseline import CPSATSolver

    slots = [Slot("segunda", h) for h in range(8, 18)]
    profs = {
        "P1": _prof("P1", slots),
        "P2": _prof("P2", slots),
    }
    salas = {"S1": _sala("S1"), "S2": _sala("S2")}
    turmas = {"T1": _turma("T1", alunos=30)}
    disciplinas = {"D1": _disc("D1", carga=1)}
    subgrupos = {
        "SG1": Subgrupo(identificador="SG1", turma_pai="T1", nome="Grupo A", numero_alunos=15),
        "SG2": Subgrupo(identificador="SG2", turma_pai="T1", nome="Grupo B", numero_alunos=15),
    }

    curriculo = [
        EntradaCurricular("T1", "D1", professores_elegiveis=("P1",), subgrupo_id="SG1"),
        EntradaCurricular("T1", "D1", professores_elegiveis=("P2",), subgrupo_id="SG2"),
    ]

    problema = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
        subgrupos=subgrupos,
    )

    ctx = problema.para_contexto()
    solver = CPSATSolver()

    if not solver.esta_disponivel():
        pytest.skip("ortools não disponível")

    # Construir seed com sobreposição proposital para testar H03
    horario_inicial = Horario()
    horario_inicial.adicionar(Aula("T1", "D1", "P1", "S1", Slot("segunda", 8), subgrupo_id="SG1"))
    horario_inicial.adicionar(Aula("T1", "D1", "P2", "S2", Slot("segunda", 8), subgrupo_id="SG2"))  # OK: subgrupos diferentes
    # Não adicionar turma inteira no mesmo slot

    resultado = solver.resolver(horario_inicial, ctx, tempo_limite_segundos=10.0)

    from timetable.constraints import verificar_hard

    violacoes = verificar_hard(resultado, ctx)
    h03_violacoes = [v for v in violacoes if v.startswith("H03:")]
    assert h03_violacoes == [], f"H03 violado no CP-SAT: {h03_violacoes}"