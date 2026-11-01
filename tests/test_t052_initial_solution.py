"""Teste de regressão T052: solução inicial viável e uso do horário_inicial."""

from __future__ import annotations

from timetable.domain import (
    EntradaCurricular,
    construir_problema,
)
from timetable.seed import construir_solucao_inicial
from timetable.models import Professor, Sala, Slot, Turma, Disciplina


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


def test_construir_solucao_inicial_coloca_todas_sessoes() -> None:
    """Solução inicial coloca todas as sessões requeridas sem violar restrições duras."""

    profs = {"P1": _prof("P1", [Slot("segunda", h) for h in range(8, 18)])}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disc("D1", carga=3)}
    curriculo = [EntradaCurricular("T1", "D1", professores_elegiveis=("P1",))]

    problema = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )
    assert not problema.tem_erros
    assert len(problema.sessoes) == 3

    slots = [Slot("segunda", h) for h in range(8, 18)]
    horario = construir_solucao_inicial(problema, slots, rng=None)

    # Verificar que todas as 3 sessões foram colocadas
    assert len(horario.aulas) == 3
    # Verificar restrições duras
    from timetable.constraints import verificar_hard

    ctx = problema.para_contexto()
    violacoes = verificar_hard(horario, ctx)
    assert violacoes == [], f"Violações duras: {violacoes}"


def test_construir_solucao_inicial_respeita_indisponibilidade() -> None:
    """Sessões não são colocadas em slots indisponíveis."""

    # Prof disponível apenas terça
    profs = {"P1": _prof("P1", [Slot("terca", h) for h in range(8, 18)])}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disc("D1", carga=2)}
    curriculo = [EntradaCurricular("T1", "D1", professores_elegiveis=("P1",))]

    problema = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )

    # Slots segunda a sexta
    slots = [Slot(d, h) for d in ["segunda", "terca", "quarta", "quinta", "sexta"] for h in range(8, 18)]
    horario = construir_solucao_inicial(problema, slots, rng=None)

    # Todas as aulas devem ser na terça
    for aula in horario.aulas:
        assert aula.slot.dia == "terca"


def test_solucao_inicial_sem_professor_elegivel_falha() -> None:
    """Sem professor elegível (qualificações definidas mas vazias), o problema tem erro."""

    # Professor sem qualificação para D1 (qualificacoes_definidas=True, qualificacoes vazias)
    profs = {
        "P1": Professor(
            identificador="P1",
            nome="Prof P1",
            disponibilidade=frozenset(),
            qualificacoes=frozenset(),
            qualificacoes_definidas=True,
        )
    }
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disc("D1")}
    curriculo = [EntradaCurricular("T1", "D1")]  # sem professores_elegiveis

    problema = construir_problema(
        professores=profs,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        curriculo=curriculo,
    )

    assert problema.tem_erros
    assert any(d.codigo == "SEM_PROFESSOR_ELEGIVEL" for d in problema.diagnosticos)