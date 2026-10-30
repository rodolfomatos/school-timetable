#!/usr/bin/env python3
"""Benchmark de performance com dados reais de escola.

Executa CP-SAT, Simulated Annealing e Tabu Search com o dataset
data/real_school.json e mede tempo de execução e qualidade da solução.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from timetable.constraints import (
    ContextoRestricoes,
    verificar_hard,
    calcular_penalidades_moles,
)
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


def carregar_dataset(caminho: str) -> tuple[dict, dict, dict, dict, list, list]:
    """Carrega o dataset JSON e retorna dicionários de entidades."""

    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))

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

    casamentos = [
        type("RelacaoCasamento", (), {"professor_a": c["professor_a"], "professor_b": c["professor_b"]})()
        for c in dados.get("casamentos", [])
    ]

    relacoes_filho = [
        type("RelacaoFilho", (), {
            "professor_pai": r["professor_pai"],
            "professor_mae": r["professor_mae"],
            "identificador_turma_filho": r["identificador_turma_filho"],
        })()
        for r in dados.get("relacoes_filho", [])
    ]

    return professores, salas, turmas, disciplinas, casamentos, relacoes_filho


def gerar_slots(dados: dict) -> list[Slot]:
    """Gera lista de slots a partir do dataset."""

    slots = []
    for s in dados["slots"]:
        slots.append(Slot(dia=s["dia"], hora=s["hora"]))
    return slots


def construir_ctx(
    professores: dict,
    salas: dict,
    turmas: dict,
    disciplinas: dict,
    casamentos: list,
    relacoes_filho: list,
) -> ContextoRestricoes:
    """Constrói o ContextoRestricoes a partir dos dicionários."""

    # Converter casamentos para objetos com atributos
    casamentos_obj = []
    for c in casamentos:
        casamentos_obj.append(
            type("RelacaoCasamento", (), {
                "professor_a": c.professor_a,
                "professor_b": c.professor_b,
            })()
        )

    relacoes_filho_obj = []
    for r in relacoes_filho:
        relacoes_filho_obj.append(
            type("RelacaoFilho", (), {
                "professor_pai": r.professor_pai,
                "professor_mae": r.professor_mae,
                "identificador_turma_filho": r.identificador_turma_filho,
            })()
        )

    return ContextoRestricoes(
        professores=professores,
        salas=salas,
        turmas=turmas,
        disciplinas=disciplinas,
        casamentos=casamentos_obj,
        relacoes_filho=relacoes_filho_obj,
    )


def executar_cp_sat(
    horario_inicial: Horario,
    ctx: ContextoRestricoes,
    tempo_limite: float,
) -> tuple[Horario, float, str]:
    """Executa CP-SAT e retorna (horario, tempo, status)."""

    solver = CPSATSolver()
    if not solver.esta_disponivel():
        return horario_inicial.clone(), 0.0, "ortools_nao_disponivel"

    inicio = time.time()
    resultado = solver.resolver(horario_inicial, ctx, tempo_limite=tempo_limite)
    tempo = time.time() - inicio
    av = avaliar(resultado, ctx)
    status = "viavel" if av.viavel else "inviavel"
    return resultado, tempo, status


def executar_sa(
    horario_inicial: Horario,
    ctx: ContextoRestricoes,
    slots: list[Slot],
    tempo_limite: float,
) -> tuple[Horario, float, str]:
    """Executa Simulated Annealing e retorna (horario, tempo, status)."""

    inicio = time.time()
    resultado = simulated_annealing(
        horario_inicial=horario_inicial,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=tempo_limite,
        semente=42,
    )
    tempo = time.time() - inicio
    av = avaliar(resultado, ctx)
    status = "viavel" if av.viavel else "inviavel"
    return resultado, tempo, status


def executar_ts(
    horario_inicial: Horario,
    ctx: ContextoRestricoes,
    slots: list[Slot],
    tempo_limite: float,
) -> tuple[Horario, float, str]:
    """Executa Tabu Search e retorna (horario, tempo, status)."""

    inicio = time.time()
    resultado = tabu_search(
        horario_inicial=horario_inicial,
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=tempo_limite,
        semente=42,
    )
    tempo = time.time() - inicio
    av = avaliar(resultado, ctx)
    status = "viavel" if av.viavel else "inviavel"
    return resultado, tempo, status


def main() -> None:
    """Executa o benchmark completo."""

    dados_caminho = "data/real_school.json"
    professores, salas, turmas, disciplinas, casamentos, relacoes_filho = carregar_dataset(
        dados_caminho
    )
    slots = gerar_slots(
        {"slots": [{"dia": s["dia"], "hora": s["hora"]} for s in json.loads(
            Path(dados_caminho).read_text(encoding="utf-8")
        )["slots"]]}
    )
    ctx = construir_ctx(professores, salas, turmas, disciplinas, casamentos, relacoes_filho)

    # Contar aulas necessárias
    total_aulas_necessarias = sum(
        d.carga_semanal for d in disciplinas.values()
    ) * len(turmas)
    print(f"Total de aulas necessárias: {total_aulas_necessarias}")
    print(f"Total de slots: {len(slots)}")
    print(f"Total de professores: {len(professores)}")
    print(f"Total de salas: {len(salas)}")
    print(f"Total de turmas: {len(turmas)}")
    print()

    horario_vazio = Horario()

    # Executar CP-SAT
    print("=== CP-SAT ===")
    resultado_cp, tempo_cp, status_cp = executar_cp_sat(
        horario_vazio, ctx, tempo_limite=60.0
    )
    av_cp = avaliar(resultado_cp, ctx)
    print(f"Tempo: {tempo_cp:.2f}s")
    print(f"Status: {status_cp}")
    print(f"Score: {av_cp.score}")
    print(f"Violações duras: {len(av_cp.violacoes_hard)}")
    print(f"Penalidades moles: {av_cp.penalidades_moles}")
    print(f"Aulas agendadas: {len(resultado_cp.aulas)}")
    print()

    # Executar Simulated Annealing
    print("=== Simulated Annealing ===")
    resultado_sa, tempo_sa, status_sa = executar_sa(
        horario_vazio, ctx, slots, tempo_limite=60.0
    )
    av_sa = avaliar(resultado_sa, ctx)
    print(f"Tempo: {tempo_sa:.2f}s")
    print(f"Status: {status_sa}")
    print(f"Score: {av_sa.score}")
    print(f"Violações duras: {len(av_sa.violacoes_hard)}")
    print(f"Penalidades moles: {av_sa.penalidades_moles}")
    print(f"Aulas agendadas: {len(resultado_sa.aulas)}")
    print()

    # Executar Tabu Search
    print("=== Tabu Search ===")
    resultado_ts, tempo_ts, status_ts = executar_ts(
        horario_vazio, ctx, slots, tempo_limite=60.0
    )
    av_ts = avaliar(resultado_ts, ctx)
    print(f"Tempo: {tempo_ts:.2f}s")
    print(f"Status: {status_ts}")
    print(f"Score: {av_ts.score}")
    print(f"Violações duras: {len(av_ts.violacoes_hard)}")
    print(f"Penalidades moles: {av_ts.penalidades_moles}")
    print(f"Aulas agendadas: {len(resultado_ts.aulas)}")
    print()

    # Resumo
    print("=== RESUMO ===")
    print(f"{'Solver':<20} {'Tempo(s)':<10} {'Status':<10} {'Score':<10} {'Hard':<8} {'Soft':<8} {'Aulas':<8}")
    print("-" * 80)
    print(f"{'CP-SAT':<20} {tempo_cp:<10.2f} {status_cp:<10} {av_cp.score:<10} {len(av_cp.violacoes_hard):<8} {av_cp.penalidades_moles:<8} {len(resultado_cp.aulas):<8}")
    print(f"{'Simulated Annealing':<20} {tempo_sa:<10.2f} {status_sa:<10} {av_sa.score:<10} {len(av_sa.violacoes_hard):<8} {av_sa.penalidades_moles:<8} {len(resultado_sa.aulas):<8}")
    print(f"{'Tabu Search':<20} {tempo_ts:<10.2f} {status_ts:<10} {av_ts.score:<10} {len(av_ts.violacoes_hard):<8} {av_ts.penalidades_moles:<8} {len(resultado_ts.aulas):<8}")


if __name__ == "__main__":
    main()
