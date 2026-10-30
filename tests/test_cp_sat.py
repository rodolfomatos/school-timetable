"""Testes para o solver CP-SAT (linha de base exata).

Os testes funcionam tanto com `ortools` instalado (validação completa) como
sem ele (fallback graceful).
"""

import pytest

from timetable.constraints import ContextoRestricoes, calcular_penalidades_moles, verificar_hard
from timetable.cp_sat_baseline import CPSATSolver
from timetable.objective import avaliar
from timetable.models import (
    Aula,
    Disciplina,
    Horario,
    Professor,
    Sala,
    Slot,
    Turma,
)


def _ctx_minimo() -> ContextoRestricoes:
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
        },
        disciplinas={
            "m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=1),
        },
        casamentos=[],
        relacoes_filho=[],
    )


def _horario_vazio() -> Horario:
    return Horario()


def test_cp_sat_fallback_sem_ortools_devolve_copia():
    """Quando ortools não está instalado, o solver devolve uma cópia do inicial."""

    solver = CPSATSolver()
    if solver.esta_disponivel():
        pytest.skip("ortools está instalado; teste de fallback não aplicável")

    h0 = _horario_vazio()
    h0.adicionar(
        Aula(
            turma="t1",
            disciplina="m1",
            professor="p1",
            sala="s1",
            slot=Slot(dia="segunda", hora=1),
        )
    )
    ctx = _ctx_minimo()
    resultado = solver.resolver(h0, ctx, tempo_limite_segundos=5.0)

    # Deve ser uma cópia distinta do objeto original
    assert resultado is not h0
    assert len(resultado.aulas) == len(h0.aulas)
    assert len(resultado.aulas) == 1


@pytest.mark.skipif(not CPSATSolver().esta_disponivel(), reason="ortools não instalado")
def test_cp_sat_respeita_restricoes_duras():
    """Com ortools disponível, a solução não viola restrições duras."""

    solver = CPSATSolver()
    h0 = _horario_vazio()
    ctx = _ctx_minimo()
    slots = [Slot(dia="segunda", hora=h) for h in range(1, 5)]

    # Adiciona algumas aulas de seed para reduzir o espaço
    for slot in slots:
        h0.adicionar(
            Aula(
                turma="t1",
                disciplina="m1",
                professor="p1",
                sala="s1",
                slot=slot,
            )
        )

    resultado = solver.resolver(h0, ctx, tempo_limite_segundos=10.0)
    violacoes = verificar_hard(resultado, ctx)
    assert violacoes == [], f"Violações duras encontradas: {violacoes}"


@pytest.mark.skipif(not CPSATSolver().esta_disponivel(), reason="ortools não instalado")
def test_cp_sat_nao_duplica_professor_no_mesmo_slot():
    """Com ortools, o mesmo professor não dá duas aulas no mesmo slot."""

    solver = CPSATSolver()
    h0 = _horario_vazio()
    ctx = _ctx_minimo()
    resultado = solver.resolver(h0, ctx, tempo_limite_segundos=10.0)

    professor_slot: dict[tuple[str, Slot], int] = {}
    for aula in resultado.aulas:
        chave = (aula.professor, aula.slot)
        professor_slot[chave] = professor_slot.get(chave, 0) + 1
    for count in professor_slot.values():
        assert count <= 1


@pytest.mark.skipif(not CPSATSolver().esta_disponivel(), reason="ortools não instalado")
def test_cp_sat_nao_duplica_sala_no_mesmo_slot():
    """Com ortools, a mesma sala não alberga duas aulas no mesmo slot."""

    solver = CPSATSolver()
    h0 = _horario_vazio()
    ctx = _ctx_minimo()
    resultado = solver.resolver(h0, ctx, tempo_limite_segundos=10.0)

    sala_slot: dict[tuple[str, Slot], int] = {}
    for aula in resultado.aulas:
        chave = (aula.sala, aula.slot)
        sala_slot[chave] = sala_slot.get(chave, 0) + 1
    for count in sala_slot.values():
        assert count <= 1


# --- Testes que funcionam sem ortools (métodos estáticos e construtor) ---


def test_cp_sat_esta_disponivel_retorna_bool():
    """esta_disponivel() deve retornar um booleano."""

    solver = CPSATSolver()
    resultado = solver.esta_disponivel()
    assert isinstance(resultado, bool)
    # Como ortools está instalado neste ambiente, deve ser True
    assert resultado is True


def test_cp_sat_fallback_devolve_copia_mesmo_com_ortools():
    """O solver devolve uma cópia distinta do horário inicial."""

    solver = CPSATSolver()
    h0 = Horario()
    h0.adicionar(
        Aula(
            turma="t1",
            disciplina="m1",
            professor="p1",
            sala="s1",
            slot=Slot(dia="segunda", hora=1),
        )
    )
    ctx = _ctx_minimo()
    resultado = solver.resolver(h0, ctx, tempo_limite_segundos=5.0)

    assert resultado is not h0
    assert len(resultado.aulas) == 1
    assert resultado.aulas[0].turma == "t1"
    assert resultado.aulas[0].professor == "p1"


def test_gerar_slots_com_disponibilidades():
    """_gerar_slots usa as disponibilidades dos professores quando disponíveis."""

    profs = {
        "p1": Professor(
            identificador="p1",
            nome="Prof. Um",
            disponibilidade=frozenset({Slot(dia="segunda", hora=1), Slot(dia="terca", hora=2)}),
        ),
    }
    salas = {}
    slots = CPSATSolver._gerar_slots(profs, salas)
    slot_set = {(s.dia, s.hora) for s in slots}
    assert ("segunda", 1) in slot_set
    assert ("terca", 2) in slot_set


def test_gerar_slots_padrao_sem_disponibilidades():
    """_gerar_slots usa um padrão padrão quando não há disponibilidades."""

    profs = {
        "p1": Professor(identificador="p1", nome="Prof. Um"),
    }
    salas = {}
    slots = CPSATSolver._gerar_slots(profs, salas)
    assert len(slots) > 0
    # Deve conter segunda a sexta, 8h-17h
    assert Slot(dia="segunda", hora=8) in slots
    assert Slot(dia="sexta", hora=17) in slots


def test_cp_sat_resolver_sem_ortools_devolve_copia_mesmo_com_aulas():
    """Fallback devolve uma cópia distinta mesmo quando o horário tem aulas."""

    solver = CPSATSolver()
    h0 = Horario()
    h0.adicionar(
        Aula(
            turma="t1",
            disciplina="m1",
            professor="p1",
            sala="s1",
            slot=Slot(dia="segunda", hora=1),
        )
    )
    ctx = _ctx_minimo()
    resultado = solver.resolver(h0, ctx, tempo_limite_segundos=5.0)

    assert resultado is not h0
    assert len(resultado.aulas) == 1
    assert resultado.aulas[0].turma == "t1"
    assert resultado.aulas[0].professor == "p1"


# --- Testes para F-004 e F-005: CP-SAT S09/S10 com condição de limiar ---


@pytest.mark.skipif(not CPSATSolver().esta_disponivel(), reason="ortools não instalado")
def test_cp_sat_s09_diferenca_pequena_nao_penaliza():
    """S09: diferença <= 2 entre professores não deve gerar penalidade."""

    solver = CPSATSolver()
    ctx = ContextoRestricoes(
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
        },
        disciplinas={
            "m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=2),
        },
        casamentos=[],
        relacoes_filho=[],
    )
    [Slot(dia="segunda", hora=h) for h in range(1, 5)]

    # Cada professor tem 1 aula (diferença = 0, <= 2)
    h0 = Horario()
    h0.adicionar(Aula("t1", "m1", "p1", "s1", Slot(dia="segunda", hora=1)))
    h0.adicionar(Aula("t1", "m1", "p2", "s2", Slot(dia="segunda", hora=2)))

    resultado = solver.resolver(h0, ctx, tempo_limite_segundos=10.0)
    avaliar(resultado, ctx)
    # Não deve haver penalidade S09 (diferença <= 2)
    s09_penalidades = [
        p for p in calcular_penalidades_moles(resultado, ctx) if p.id_restricao == "S09"
    ]
    assert len(s09_penalidades) == 0


@pytest.mark.skipif(not CPSATSolver().esta_disponivel(), reason="ortools não instalado")
def test_cp_sat_s10_menos_de_5_aulas_por_dia_nao_penaliza():
    """S10: menos de 5 aulas de um professor num único dia não deve gerar penalidade."""

    solver = CPSATSolver()
    ctx = ContextoRestricoes(
        professores={
            "p1": Professor(identificador="p1", nome="Prof. Um"),
        },
        salas={
            "s1": Sala(identificador="s1", capacidade=30),
        },
        turmas={
            "t1": Turma(identificador="t1", ano=10, numero_alunos=25),
        },
        disciplinas={
            "m1": Disciplina(identificador="m1", nome="Matemática", carga_semanal=3),
        },
        casamentos=[],
        relacoes_filho=[],
    )
    [Slot(dia="segunda", hora=h) for h in range(1, 5)]

    # 3 aulas no mesmo dia (< 5, não deve penalizar S10)
    h0 = Horario()
    for hora in [1, 2, 3]:
        h0.adicionar(Aula("t1", "m1", "p1", "s1", Slot(dia="segunda", hora=hora)))

    resultado = solver.resolver(h0, ctx, tempo_limite_segundos=10.0)
    avaliar(resultado, ctx)
    s10_penalidades = [
        p for p in calcular_penalidades_moles(resultado, ctx) if p.id_restricao == "S10"
    ]
    assert len(s10_penalidades) == 0


@pytest.mark.skipif(not CPSATSolver().esta_disponivel(), reason="ortools não instalado")
def test_cp_sat_resolve_instancia_multiplos_professores():
    """CP-SAT resolve instância com múltiplos professores e disciplinas sem crashar."""

    solver = CPSATSolver()
    ctx = ContextoRestricoes(
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
    resultado = solver.resolver(Horario(), ctx, tempo_limite_segundos=10.0)
    violacoes = verificar_hard(resultado, ctx)
    assert violacoes == [], f"Violações duras: {violacoes}"
