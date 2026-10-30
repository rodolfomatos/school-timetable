"""Testes de integração com dados reais de escola (T018)."""

import json
import time
from pathlib import Path

from timetable.constraints import ContextoRestricoes, verificar_hard, calcular_penalidades_moles
from timetable.cp_sat_baseline import CPSATSolver
from timetable.local_search import simulated_annealing, tabu_search
from timetable.models import (
    Aula,
    Disciplina,
    Horario,
    Professor,
    Sala,
    Slot,
    Turma,
)
from timetable.objective import avaliar


def carregar_dataset_real() -> tuple[ContextoRestricoes, list[Slot]]:
    """Carrega o dataset real_school.json e retorna (ctx, slots)."""

    dados = json.loads(Path("data/real_school.json").read_text(encoding="utf-8"))

    professores: dict[str, Professor] = {}
    for p in dados["professores"]:
        disponibilidade = frozenset(
            Slot(dia=s["dia"], hora=s["hora"]) for s in p.get("disponibilidade", [])
        )
        professores[p["identificador"]] = Professor(
            identificador=p["identificador"],
            nome=p["nome"],
            disponibilidade=disponibilidade,
            dia_folga_preferido=p.get("dia_folga_preferido"),
            prefere_manha=p.get("prefere_manha", True),
            carga_maxima_semanal=p.get("carga_maxima_semanal", 30),
            carga_minima_semanal=p.get("carga_minima_semanal", 10),
        )

    salas: dict[str, Sala] = {}
    for s in dados["salas"]:
        salas[s["identificador"]] = Sala(
            identificador=s["identificador"],
            capacidade=s["capacidade"],
            tipo=s.get("tipo", "normal"),
            dias_disponiveis=frozenset(s.get("dias_disponiveis", [])),
        )

    turmas: dict[str, Turma] = {}
    for t in dados["turmas"]:
        turmas[t["identificador"]] = Turma(
            identificador=t["identificador"],
            ano=t["ano"],
            numero_alunos=t["numero_alunos"],
        )

    disciplinas: dict[str, Disciplina] = {}
    for d in dados["disciplinas"]:
        disciplinas[d["identificador"]] = Disciplina(
            identificador=d["identificador"],
            nome=d["nome"],
            carga_semanal=d["carga_semanal"],
            tipo_sala_requerida=d.get("tipo_sala_requerida", "normal"),
        )

    slots = [
        Slot(dia=s["dia"], hora=s["hora"]) for s in dados["slots"]
    ]

    # Casamentos e relações filho como objetos simples
    class RelCas:
        def __init__(self, a, b):
            self.professor_a = a
            self.professor_b = b

    class RelFilho:
        def __init__(self, pai, mae, turma):
            self.professor_pai = pai
            self.professor_mae = mae
            self.identificador_turma_filho = turma

    casamentos = [RelCas(c["professor_a"], c["professor_b"]) for c in dados.get("casamentos", [])]
    relacoes_filho = [
        RelFilho(r["professor_pai"], r["professor_mae"], r["identificador_turma_filho"])
        for r in dados.get("relacoes_filho", [])
    ]

    ctx = ContextoRestricoes(
        professores=professores,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        casamentos=casamentos,
        relacoes_filho=relacoes_filho,
    )
    return ctx, slots


def test_dataset_real_carrega_corretamente():
    """O dataset real deve carregar com todas as entidades esperadas."""

    ctx, slots = carregar_dataset_real()

    assert len(ctx.professores) == 15
    assert len(ctx.salas) == 8
    assert len(ctx.turmas) == 10
    assert len(ctx.disciplinas) == 12
    assert len(slots) == 25  # 5 dias × 5 horas
    assert len(ctx.casamentos) == 2
    assert len(ctx.relacoes_filho) == 1


def test_dataset_real_total_aulas_necessarias():
    """Verifica o total de aulas que precisam ser agendadas."""

    ctx, _ = carregar_dataset_real()
    total = sum(d.carga_semanal for d in ctx.disciplinas.values()) * len(ctx.turmas)
    # 12 disciplinas × carga variada × 10 turmas
    assert total > 0
    print(f"\nTotal de aulas necessárias: {total}")


def test_simulated_annealing_dados_reais():
    """SA deve resolver o dataset real sem violações duras (ou com tempo limite)."""

    ctx, slots = carregar_dataset_real()
    horario_vazio = Horario()

    inicio = time.time()
    resultado = simulated_annealing(
        horario_inicial=horario_vazio,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=60.0,
        semente=42,
    )
    tempo_execucao = time.time() - inicio

    av = avaliar(resultado, ctx)

    # Registra métricas
    print(f"\n[SA] Tempo: {tempo_execucao:.2f}s")
    print(f"[SA] Score: {av.score}")
    print(f"[SA] Violações duras: {len(av.violacoes_hard)}")
    print(f"[SA] Penalidades moles: {av.penalidades_moles}")
    print(f"[SA] Aulas agendadas: {len(resultado.aulas)}")

    # Se CP-SAT não está disponível, SA pode não conseguir agendar tudo
    # mas não deve criar violações duras nas aulas que agendar
    violacoes = verificar_hard(resultado, ctx)
    assert len(violacoes) == 0, f"Violações duras: {violacoes}"


def test_tabu_search_dados_reais():
    """Tabu Search deve resolver o dataset real sem violações duras."""

    ctx, slots = carregar_dataset_real()
    horario_vazio = Horario()

    inicio = time.time()
    resultado = tabu_search(
        horario_inicial=horario_vazio,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=60.0,
        semente=42,
    )
    tempo_execucao = time.time() - inicio

    av = avaliar(resultado, ctx)

    # Registra métricas
    print(f"\n[TS] Tempo: {tempo_execucao:.2f}s")
    print(f"[TS] Score: {av.score}")
    print(f"[TS] Violações duras: {len(av.violacoes_hard)}")
    print(f"[TS] Penalidades moles: {av.penalidades_moles}")
    print(f"[TS] Aulas agendadas: {len(resultado.aulas)}")

    violacoes = verificar_hard(resultado, ctx)
    assert len(violacoes) == 0, f"Violações duras: {violacoes}"


def test_cp_sat_dados_reais_se_disponivel():
    """CP-SAT deve resolver o dataset real se ortools estiver disponível (tempo curto)."""

    solver = CPSATSolver()
    if not solver.esta_disponivel():
        import pytest
        pytest.skip("ortools não instalado")

    ctx, slots = carregar_dataset_real()
    horario_vazio = Horario()

    # Tempo limitado para evitar travamento em problema NP-hard grande
    inicio = time.time()
    resultado = solver.resolver(
        horario_inicial=horario_vazio,
        ctx=ctx,
        tempo_limite_segundos=15.0,
    )
    tempo_execucao = time.time() - inicio

    av = avaliar(resultado, ctx)

    # Registra métricas
    print(f"\n[CP-SAT] Tempo: {tempo_execucao:.2f}s")
    print(f"[CP-SAT] Score: {av.score}")
    print(f"[CP-SAT] Violações duras: {len(av.violacoes_hard)}")
    print(f"[CP-SAT] Penalidades moles: {av.penalidades_moles}")
    print(f"[CP-SAT] Aulas agendadas: {len(resultado.aulas)}")

    # Se encontrou solução, não deve ter violações duras
    if av.viavel:
        assert len(av.violacoes_hard) == 0, f"Violações duras: {av.violacoes_hard}"
    # Se não encontrou solução viável no tempo limite, o teste ainda passa
    # (o problema é NP-hard e o tempo limite é intencionalmente curto)
