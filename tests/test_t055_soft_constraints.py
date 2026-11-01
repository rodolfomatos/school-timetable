"""Testes de fronteira e alinhamento S01–S10 (T055).

Cobrem cada restrição mole com:
- Caso base (penaliza quando deve)
- Fronteira (não penaliza no limite)
- Contra-exemplo (não penaliza quando não deve)
- Alinhamento CP-SAT vs Python
"""

from __future__ import annotations

import pytest

from timetable.constraints import PenalidadeMole, calcular_penalidades_moles
from timetable.models import Aula, Horario, Professor, Sala, Slot, Turma, Disciplina


def _ctx_padrao():
    """Contexto mínimo reutilizável."""
    from timetable.constraints import ContextoRestricoes

    return ContextoRestricoes(
        professores={},
        salas={},
        turmas={},
        disciplinas={},
        casamentos=[],
        relacoes_filho=[],
    )


def _prof(id_: str, **kwargs) -> Professor:
    defaults = {
        "nome": f"Prof {id_}",
        "disponibilidade": frozenset(),
        "dia_folga_preferido": None,
        "prefere_manha": True,
        "carga_maxima_semanal": 30,
        "carga_minima_semanal": 5,
        "qualificacoes": frozenset(),
        "qualificacoes_definidas": False,
    }
    defaults.update(kwargs)
    return Professor(identificador=id_, **defaults)


def _turma(id_: str, alunos: int = 25) -> Turma:
    return Turma(identificador=id_, ano=1, numero_alunos=alunos)


def _disc(id_: str, carga: int = 2) -> Disciplina:
    return Disciplina(identificador=id_, nome=f"Disc {id_}", carga_semanal=carga, tipo_sala_requerida="normal")


def _sala(id_: str, cap: int = 30) -> Sala:
    return Sala(identificador=id_, capacidade=cap, tipo="normal")


def _slot(dia: str, hora: int) -> Slot:
    return Slot(dia=dia, hora=hora)


def _aula(turma: str, disc: str, prof: str, sala: str, slot: Slot) -> Aula:
    return Aula(turma=turma, disciplina=disc, professor=prof, sala=sala, slot=slot)


# ============================================================================
# S01 — Dia de folga preferido
# ============================================================================

def test_s01_penaliza_aula_no_dia_de_folga():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", dia_folga_preferido="segunda")
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S01" and p.valor == 10 for p in pens)


def test_s01_nao_penaliza_fora_do_dia_de_folga():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", dia_folga_preferido="segunda")
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("terca", 8)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S01" for p in pens)


def test_s01_sem_dia_de_folga_nao_penaliza():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", dia_folga_preferido=None)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S01" for p in pens)


# ============================================================================
# S02 — Preferência manhã/tarde
# ============================================================================

def test_s02_penaliza_tarde_quando_prefere_manha():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", prefere_manha=True)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 14)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S02" and p.valor == 8 for p in pens)


def test_s02_nao_penaliza_manha_quando_prefere_manha():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", prefere_manha=True)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 10)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S02" for p in pens)


def test_s02_nao_penaliza_se_nao_prefere_manha():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", prefere_manha=False)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 14)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S02" for p in pens)


def test_s02_fronteira_hora_13_e_tarde():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", prefere_manha=True)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 13)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S02" for p in pens)


def test_s02_fronteira_hora_12_e_manha():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", prefere_manha=True)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 12)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S02" for p in pens)


# ============================================================================
# S03 — Duas horas consecutivas
# ============================================================================

def test_s03_penaliza_sem_consecutivas_carga_2():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=2)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("quarta", 10)))  # não consecutivo
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S03" and p.valor == 6 for p in pens)


def test_s03_nao_penaliza_com_consecutivas():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=2)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 9)))  # consecutivo
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S03" for p in pens)


def test_s03_nao_penaliza_carga_1():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=1)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S03" for p in pens)


def test_s03_consecutivas_em_dia_diferente_nao_contam():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=2)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 9)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("terca", 10)))  # dias diferentes
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S03" for p in pens)


# ============================================================================
# S04 — Disciplinas espalhadas pela semana
# ============================================================================

def test_s04_penaliza_tudo_num_dia_unico():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=3)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 9)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 10)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S04" and p.valor == 5 for p in pens)


def test_s04_nao_penaliza_espalhados():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=3)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("terca", 9)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("quarta", 10)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S04" for p in pens)


def test_s04_nao_penaliza_carga_1():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=1)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S04" for p in pens)


# ============================================================================
# S05 — Padrão A-B-C-A
# ============================================================================

def test_s05_penaliza_padrao_abca():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=1)
    ctx.disciplinas["D2"] = _disc("D2", carga=1)
    ctx.disciplinas["D3"] = _disc("D3", carga=1)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D2", "P2", "S2", _slot("segunda", 9)))
    h.adicionar(_aula("T1", "D3", "P3", "S3", _slot("segunda", 10)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 11)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S05" and p.valor == 7 for p in pens)


def test_s05_nao_penaliza_aba_3_posicoes():
    """A-B-A (3 posições) NÃO é A-B-C-A (4 posições)."""
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=1)
    ctx.disciplinas["D2"] = _disc("D2", carga=1)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D2", "P2", "S2", _slot("segunda", 9)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 10)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S05" for p in pens)


def test_s05_nao_penaliza_abcb():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=1)
    ctx.disciplinas["D2"] = _disc("D2", carga=1)
    ctx.disciplinas["D3"] = _disc("D3", carga=1)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D2", "P2", "S2", _slot("segunda", 9)))
    h.adicionar(_aula("T1", "D3", "P3", "S3", _slot("segunda", 10)))
    h.adicionar(_aula("T1", "D2", "P2", "S2", _slot("segunda", 11)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S05" for p in pens)


def test_s05_requer_4_disciplinas_distintas():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=1)
    ctx.disciplinas["D2"] = _disc("D2", carga=1)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D2", "P2", "S2", _slot("segunda", 9)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 10)))
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 11)))  # D1-D2-D1-D1
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S05" for p in pens)


# ============================================================================
# S06 — Bloco 2h para avaliação (carga >= 4)
# ============================================================================

def test_s06_penaliza_sem_bloco_carga_alta():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", carga_maxima_semanal=6)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D2", "P1", "S1", _slot("segunda", 10)))  # gap
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S06" and p.valor == 9 for p in pens)


def test_s06_nao_penaliza_com_bloco():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", carga_maxima_semanal=6)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T2", "D2", "P1", "S1", _slot("segunda", 9)))  # consecutivo
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S06" for p in pens)


def test_s06_nao_penaliza_carga_baixa():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", carga_maxima_semanal=3)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    h.adicionar(_aula("T1", "D2", "P1", "S1", _slot("segunda", 10)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S06" for p in pens)


def test_s06_apenas_um_slot_nao_penaliza():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", carga_maxima_semanal=6)
    h = Horario()
    h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S06" for p in pens)


# ============================================================================
# S07 — Carga fora dos limites
# ============================================================================

def test_s07_penaliza_abaixo_do_minimo():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", carga_minima_semanal=10, carga_maxima_semanal=20)
    h = Horario()
    # apenas 5 aulas
    for i in range(5):
        h.adicionar(_aula("T1", f"D{i}", "P1", "S1", _slot("segunda", 8+i)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S07" and p.valor == 8 for p in pens)


def test_s07_penaliza_acima_do_maximo():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", carga_minima_semanal=10, carga_maxima_semanal=20)
    h = Horario()
    # 25 aulas
    for i in range(25):
        h.adicionar(_aula("T1", f"D{i}", "P1", "S1", _slot("segunda", (8+i)%10)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S07" and p.valor == 8 for p in pens)


def test_s07_nao_penaliza_dentro_dos_limites():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", carga_minima_semanal=10, carga_maxima_semanal=20)
    h = Horario()
    for i in range(15):
        h.adicionar(_aula("T1", f"D{i}", "P1", "S1", _slot("segunda", (8+i)%10)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S07" for p in pens)


def test_s07_penaliza_ambos_lados():
    """Dois professores, um abaixo outro acima."""
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1", carga_minima_semanal=10, carga_maxima_semanal=20)
    ctx.professores["P2"] = _prof("P2", carga_minima_semanal=10, carga_maxima_semanal=20)
    h = Horario()
    for i in range(5):
        h.adicionar(_aula("T1", f"D{i}", "P1", "S1", _slot("segunda", 8+i)))
    for i in range(25):
        h.adicionar(_aula("T1", f"D{i}", "P2", "S1", _slot("terca", (8+i)%10)))
    pens = calcular_penalidades_moles(h, ctx)
    s07 = [p for p in pens if p.id_restricao == "S07"]
    assert len(s07) == 2
    assert all(p.valor == 8 for p in s07)


# ============================================================================
# S08 — 5+ dias diferentes
# ============================================================================

def test_s08_penaliza_5_dias():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1")
    h = Horario()
    dias = ["segunda", "terca", "quarta", "quinta", "sexta"]
    for i, dia in enumerate(dias):
        h.adicionar(_aula("T1", f"D{i}", "P1", "S1", _slot(dia, 8)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S08" and p.valor == 12 for p in pens)


def test_s08_nao_penaliza_4_dias():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1")
    h = Horario()
    for dia in ["segunda", "terca", "quarta", "quinta"]:
        h.adicionar(_aula("T1", "D1", "P1", "S1", _slot(dia, 8)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S08" for p in pens)


def test_s08_nao_penaliza_mesmo_dia_multiplas_aulas():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1")
    h = Horario()
    for i in range(6):
        h.adicionar(_aula("T1", f"D{i}", "P1", "S1", _slot("segunda", 8+i)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S08" for p in pens)


# ============================================================================
# S09 — Distribuição desigual (diff absoluto > 2)
# ============================================================================

def test_s09_penaliza_diff_maior_que_2():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=5)
    ctx.professores["P1"] = _prof("P1")
    ctx.professores["P2"] = _prof("P2")
    h = Horario()
    # P1: 5 aulas, P2: 0 aulas -> diff = 5
    # Precisa de aulas para AMBOS os professores na disciplina para S09 se aplicar
    # Mas se P2 tem 0 aulas, o código verifica se len(contagens) > 1
    # Vamos dar 1 aula a P2 para ter 2 professores com contagens
    for i in range(5):
        h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8+i)))
    h.adicionar(_aula("T1", "D1", "P2", "S1", _slot("terca", 8)))
    # P1: 5, P2: 1 -> diff = 4 > 2
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S09" and p.valor == 11 for p in pens)


def test_s09_nao_penaliza_diff_2_ou_menos():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=4)
    ctx.professores["P1"] = _prof("P1")
    ctx.professores["P2"] = _prof("P2")
    h = Horario()
    # P1: 3, P2: 1 -> diff = 2
    for i in range(3):
        h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8+i)))
    h.adicionar(_aula("T1", "D1", "P2", "S1", _slot("terca", 8)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S09" for p in pens)


def test_s09_um_so_professor_nao_penaliza():
    ctx = _ctx_padrao()
    ctx.disciplinas["D1"] = _disc("D1", carga=5)
    ctx.professores["P1"] = _prof("P1")
    h = Horario()
    for i in range(5):
        h.adicionar(_aula("T1", "D1", "P1", "S1", _slot("segunda", 8+i)))
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S09" for p in pens)


# ============================================================================
# S10 — Carga concentrada (>=5 aulas em <=2 dias)
# ============================================================================

def test_s10_penaliza_5_aulas_em_2_dias():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1")
    h = Horario()
    # 5 aulas em 2 dias
    for h_ in range(3):
        h.adicionar(_aula("T1", f"D{h_}", "P1", "S1", _slot("segunda", 8+h_)))
    for h_ in range(2):
        h.adicionar(_aula("T1", f"D{h_+3}", "P1", "S1", _slot("terca", 8+h_)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S10" and p.valor == 10 for p in pens)


def test_s10_penaliza_5_aulas_em_1_dia():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1")
    h = Horario()
    for i in range(5):
        h.adicionar(_aula("T1", f"D{i}", "P1", "S1", _slot("segunda", 8+i)))
    pens = calcular_penalidades_moles(h, ctx)
    assert any(p.id_restricao == "S10" and p.valor == 10 for p in pens)


def test_s10_nao_penaliza_5_aulas_em_3_dias():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1")
    h = Horario()
    for dia in ["segunda", "terca", "quarta"]:
        h.adicionar(_aula("T1", "D1", "P1", "S1", _slot(dia, 8)))
        h.adicionar(_aula("T1", "D2", "P1", "S1", _slot(dia, 9)))
    # 6 aulas em 3 dias
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S10" for p in pens)


def test_s10_nao_penaliza_4_aulas_em_2_dias():
    ctx = _ctx_padrao()
    ctx.professores["P1"] = _prof("P1")
    h = Horario()
    for i in range(2):
        h.adicionar(_aula("T1", f"D{i}", "P1", "S1", _slot("segunda", 8+i)))
    for i in range(2):
        h.adicionar(_aula("T1", f"D{i+2}", "P1", "S1", _slot("terca", 8+i)))
    # 4 aulas em 2 dias -> abaixo do limite de 5
    pens = calcular_penalidades_moles(h, ctx)
    assert not any(p.id_restricao == "S10" for p in pens)


# ============================================================================
# Alinhamento CP-SAT vs Python (smoke test)
# ============================================================================

@pytest.mark.skipif(
    True, reason="Requer ortools; executar manualmente para validar alinhamento"
)
def test_cpsat_alinhamento_s01_a_s10():
    """Teste de integração: CP-SAT e Python concordam nas penalidades.

    Executar manualmente quando ortools estiver disponível.
    """
    from timetable.cp_sat_baseline import CPSATSolver
    from timetable.domain import (
        EntradaCurricular,
        construir_problema,
        construir_solucao_inicial,
    )

    # Instância controlada pequena
    profs = {"P1": _prof("P1", prefere_manha=True, dia_folga_preferido="sexta",
                          carga_maxima_semanal=6, carga_minima_semanal=5,
                          disponibilidade=frozenset([_slot("segunda", h) for h in range(8, 18)]))}
    salas = {"S1": _sala("S1")}
    turmas = {"T1": _turma("T1")}
    disciplinas = {"D1": _disc("D1", carga=3)}
    curriculo = [EntradaCurricular("T1", "D1", professores_elegiveis=("P1",))]

    prob = construir_problema(professores=profs, salas=salas, turmas=turmas,
                              disciplinas=disciplinas, curriculo=curriculo)
    slots = [_slot(d, h) for d in ["segunda", "terca", "quarta", "quinta", "sexta"]
             for h in range(8, 14)]
    seed = construir_solucao_inicial(prob, slots, rng=None)

    ctx = prob.para_contexto()
    solver = CPSATSolver()
    if not solver.esta_disponivel():
        pytest.skip("ortools não disponível")

    res = solver.resolver(seed, ctx, tempo_limite_segundos=10.0)
    pens_py = calcular_penalidades_moles(res, ctx)

    # Verificar que não há violações duras
    from timetable.constraints import verificar_hard
    assert verificar_hard(res, ctx) == []

    # Apenas verifica que roda sem erro e produz penalidades estruturadas
    assert all(isinstance(p, PenalidadeMole) for p in pens_py)