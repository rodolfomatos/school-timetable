"""Teste de integração: seed + solver → horário viável."""

from timetable.constraints import ContextoRestricoes, verificar_hard
from timetable.models import (
    Aula,
    Disciplina,
    Horario,
    Professor,
    Sala,
    Slot,
    Turma,
)
from timetable.local_search import simulated_annealing, tabu_search
from timetable.objective import avaliar


def _ctx_integracao() -> ContextoRestricoes:
    return ContextoRestricoes(
        professores={
            "p1": Professor(identificador="p1", nome="Prof. Um"),
            "p2": Professor(identificador="p2", nome="Prof. Dois"),
        },
        salas={
            "s1": Sala(identificador="s1", capacidade=30),
            "s2": Sala(identificador="s2", capacidade=30),
        },
        turmas={
            "t1": Turma(identificador="t1", ano=10, numero_alunos=25),
            "t2": Turma(identificador="t2", ano=10, numero_alunos=25),
        },
        disciplinas={
            "m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=2),
            "p1": Disciplina(identificador="p1", nome="Português", carga_semanal=2),
        },
        casamentos=[],
        relacoes_filho=[],
    )


def _slots() -> list[Slot]:
    return [
        Slot(dia=dia, hora=hora) for dia in ["segunda", "terca", "quarta"] for hora in range(1, 5)
    ]


def _horario_inicial() -> Horario:
    h = Horario()
    h.adicionar(
        Aula(
            turma="t1",
            disciplina="m1",
            professor="p1",
            sala="s1",
            slot=Slot(dia="segunda", hora=1),
        )
    )
    h.adicionar(
        Aula(
            turma="t2",
            disciplina="p1",
            professor="p2",
            sala="s2",
            slot=Slot(dia="segunda", hora=2),
        )
    )
    return h


def test_simulated_annealing_nao_piora_hard():
    ctx = _ctx_integracao()
    h0 = _horario_inicial()
    resultado = simulated_annealing(
        horario_inicial=h0,
        ctx=ctx,
        slots=_slots(),
        tempo_limite_segundos=5.0,
    )
    av = avaliar(resultado, ctx)
    # O resultado não deve introduzir violações de restrições duras
    violacoes = verificar_hard(resultado, ctx)
    assert violacoes == [], f"Violações duras introduzidas pelo SA: {violacoes}"
    assert av.score > -1_000_000  # não é -infinito absoluto


def test_tabu_search_nao_piora_hard():
    ctx = _ctx_integracao()
    h0 = _horario_inicial()
    resultado = tabu_search(
        horario_inicial=h0,
        ctx=ctx,
        slots=_slots(),
        tempo_limite_segundos=5.0,
    )
    av = avaliar(resultado, ctx)
    # O resultado não deve introduzir violações de restrições duras
    violacoes = verificar_hard(resultado, ctx)
    assert violacoes == [], f"Violações duras introduzidas pelo Tabu Search: {violacoes}"
    assert av.score > -1_000_000  # não é -infinito absoluto
