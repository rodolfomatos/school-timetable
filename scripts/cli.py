#!/usr/bin/env python3
"""Interface de linha de comando para o gerador de horários escolares.

Subcomandos:
  generate  Gera um horário a partir de um dataset JSON
  validate  Valida um horário contra restrições duras
  benchmark Executa benchmark comparativo de solvers
"""

from __future__ import annotations

import argparse
import json
import sys
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
from timetable.ui import importar_json, exportar_json, gerar_grade
from timetable.export import exportar


def _carregar_dataset(caminho: str) -> tuple[ContextoRestricoes, list[Slot]]:
    """Carrega um dataset JSON e retorna (ctx, slots)."""

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

    slots = [Slot(dia=s["dia"], hora=s["hora"]) for s in dados["slots"]]

    class RelCas:
        def __init__(self, a, b):
            self.professor_a = a
            self.professor_b = b

    class RelFilho:
        def __init__(self, pai, mae, turma):
            self.professor_pai = pai
            self.professor_mae = mae
            self.identificador_turma_filho = turma

    casamentos = [
        RelCas(c["professor_a"], c["professor_b"]) for c in dados.get("casamentos", [])
    ]
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


def cmd_generate(args: argparse.Namespace) -> int:
    """Gera um horário a partir de um dataset."""

    ctx, slots = _carregar_dataset(args.input)
    horario = Horario()

    solver_name = args.solver.lower()
    tempo = args.tempo

    print(f"Carregado dataset: {args.input}")
    print(f"Solver: {solver_name}")
    print(f"Tempo limite: {tempo}s")
    print(f"Slots: {len(slots)}, Professores: {len(ctx.professores)}")
    print(f"Salas: {len(ctx.salas)}, Turmas: {len(ctx.turmas)}")
    print()

    inicio = time.time()

    if solver_name == "sa":
        resultado = simulated_annealing(
            horario_inicial=horario,
            ctx=ctx,
            slots=slots,
            tempo_limite_segundos=tempo,
            semente=42,
        )
    elif solver_name == "ts":
        resultado = tabu_search(
            horario_inicial=horario,
            ctx=ctx,
            slots=slots,
            tempo_limite_segundos=tempo,
            semente=42,
        )
    elif solver_name == "cpsat":
        solver = CPSATSolver()
        if not solver.esta_disponivel():
            print("ERRO: ortools não instalado. Use --solver sa ou --solver ts.")
            return 1
        resultado = solver.resolver(
            horario_inicial=horario,
            ctx=ctx,
            tempo_limite_segundos=tempo,
        )
    else:
        print(f"ERRO: solver desconhecido '{solver_name}'. Use sa, ts ou cpsat.")
        return 1

    tempo_execucao = time.time() - inicio
    av = avaliar(resultado, ctx)

    print(f"Tempo de execução: {tempo_execucao:.2f}s")
    print(f"Score: {av.score}")
    print(f"Violações duras: {len(av.violacoes_hard)}")
    print(f"Penalidades moles: {av.penalidades_moles}")
    print(f"Aulas agendadas: {len(resultado.aulas)}")

    if av.violacoes_hard:
        print("\nAviso: restrições duras violadas:")
        for v in av.violacoes_hard:
            print(f"  - {v}")

    # Exporta resultado
    exportar_json(resultado, args.output)
    print(f"\nHorário exportado para: {args.output}")

    # Mostra grade resumida
    grade = gerar_grade(resultado)
    print(f"\nGrade ({len(grade)} atribuições):")
    for (turma, slot), aula in sorted(grade.items()):
        print(f"  {turma} | {slot} | {aula.disciplina} | {aula.professor} | {aula.sala}")

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Valida um horário contra restrições duras."""

    horario = importar_json(args.input)

    # Precisamos de um contexto para verificar; usa um contexto vazio
    # (apenas verificações que não dependem de entidades externas)
    from timetable.constraints import ContextoRestricoes

    ctx = ContextoRestricoes(
        professores={},
        salas={},
        turmas={},
        disciplinas={},
        casamentos=[],
        relacoes_filho=[],
    )

    # Nota: sem entidades no contexto, H04-H08 não são verificáveis.
    # Esta é uma validação básica de estrutura.
    av = avaliar(horario, ctx)

    print(f"Horário: {args.input}")
    print(f"Aulas: {len(horario.aulas)}")
    print(f"Slots imutáveis: {len(horario.slots_imutaveis)}")
    print(f"Violações duras (estrutural): {len(av.violacoes_hard)}")
    print(f"Penalidades moles: {av.penalidades_moles}")

    if av.violacoes_hard:
        print("\nViolações:")
        for v in av.violacoes_hard:
            print(f"  - {v}")
        return 1

    print("\nHorário estruturalmente válido.")
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Executa benchmark comparativo de solvers."""

    ctx, slots = _carregar_dataset(args.input)
    horario = Horario()
    tempo = args.tempo

    print(f"Dataset: {args.input}")
    print(f"Slots: {len(slots)}, Professores: {len(ctx.professores)}")
    print(f"Salas: {len(ctx.salas)}, Turmas: {len(ctx.turmas)}")
    print()

    resultados = []

    # Simulated Annealing
    print("Executando Simulated Annealing...")
    inicio = time.time()
    r_sa = simulated_annealing(
        horario_inicial=horario.clone(),
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=tempo,
        semente=42,
    )
    t_sa = time.time() - inicio
    av_sa = avaliar(r_sa, ctx)
    resultados.append(("Simulated Annealing", t_sa, av_sa))

    # Tabu Search
    print("Executando Tabu Search...")
    inicio = time.time()
    r_ts = tabu_search(
        horario_inicial=horario.clone(),
        ctx=ctx,
        slots=slots,
        tempo_limite_segundos=tempo,
        semente=42,
    )
    t_ts = time.time() - inicio
    av_ts = avaliar(r_ts, ctx)
    resultados.append(("Tabu Search", t_ts, av_ts))

    # CP-SAT (se disponível)
    solver = CPSATSolver()
    if solver.esta_disponivel():
        print("Executando CP-SAT...")
        inicio = time.time()
        r_cp = solver.resolver(
            horario_inicial=horario.clone(),
            ctx=ctx,
            tempo_limite_segundos=tempo,
        )
        t_cp = time.time() - inicio
        av_cp = avaliar(r_cp, ctx)
        resultados.append(("CP-SAT", t_cp, av_cp))
    else:
        print("CP-SAT: ortools não instalado, pulando.")
        resultados.append(("CP-SAT", 0.0, None))

    print()
    print("=== RESULTADOS ===")
    print(f"{'Solver':<20} {'Tempo(s)':<10} {'Status':<10} {'Score':<10} {'Hard':<8} {'Soft':<8}")
    print("-" * 72)
    for nome, tempo_exec, av in resultados:
        if av is None:
            print(f"{nome:<20} {'N/A':<10} {'skip':<10} {'-':<10} {'-':<8} {'-':<8}")
        else:
            status = "viável" if av.viavel else "inviável"
            print(
                f"{nome:<20} {tempo_exec:<10.2f} {status:<10} "
                f"{av.score:<10} {len(av.violacoes_hard):<8} {av.penalidades_moles:<8}"
            )

    return 0


def cmd_exportar(args: argparse.Namespace) -> int:
    """Exporta um horário para CSV ou iCal."""

    horario = importar_json(args.input)

    formato = args.formato.lower()
    if formato not in ("csv", "ical", "ics"):
        print(f"ERRO: formato desconhecido '{args.formato}'. Use csv ou ical.")
        return 1

    exportar(
        horario,
        args.output,
        formato=formato,
        semana_inicial=args.semana_inicial,
        nome_escola=args.nome_escola,
    )

    print(f"Horário exportado para: {args.output} (formato: {formato})")
    return 0


def main() -> None:
    """Ponto de entrada da CLI."""

    parser = argparse.ArgumentParser(
        description="Gerador de horários escolares — school-timetable"
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comando a executar")

    # generate
    p_gen = subparsers.add_parser("generate", help="Gera um horário a partir de um dataset")
    p_gen.add_argument("--input", required=True, help="Caminho para o dataset JSON de entrada")
    p_gen.add_argument("--output", required=True, help="Caminho para o horário JSON de saída")
    p_gen.add_argument(
        "--solver", default="sa", help="Solver a usar: sa, ts ou cpsat (padrão: sa)"
    )
    p_gen.add_argument(
        "--tempo", type=float, default=60.0, help="Tempo limite em segundos (padrão: 60)"
    )
    p_gen.set_defaults(func=cmd_generate)

    # validate
    p_val = subparsers.add_parser("validate", help="Valida um horário contra restrições duras")
    p_val.add_argument("--input", required=True, help="Caminho para o horário JSON de entrada")
    p_val.set_defaults(func=cmd_validate)

    # benchmark
    p_bench = subparsers.add_parser(
        "benchmark", help="Executa benchmark comparativo de solvers"
    )
    p_bench.add_argument("--input", required=True, help="Caminho para o dataset JSON de entrada")
    p_bench.add_argument(
        "--tempo", type=float, default=30.0, help="Tempo limite por solver em segundos (padrão: 30)"
    )
    p_bench.set_defaults(func=cmd_benchmark)

    # exportar
    p_exp = subparsers.add_parser(
        "exportar", help="Exporta um horário para CSV ou iCal"
    )
    p_exp.add_argument("--input", required=True, help="Caminho para o horário JSON de entrada")
    p_exp.add_argument("--output", required=True, help="Caminho do ficheiro de saída")
    p_exp.add_argument(
        "--formato", default="csv", help="Formato de saída: csv ou ical (padrão: csv)"
    )
    p_exp.add_argument(
        "--semana-inicial", default="2026-09-07", help="Data da primeira segunda-feira (padrão: 2026-09-07)"
    )
    p_exp.add_argument(
        "--nome-escola", default="Escola", help="Nome da escola (usado no iCal)"
    )
    p_exp.set_defaults(func=cmd_exportar)

    args = parser.parse_args()

    if args.comando is None:
        parser.print_help()
        sys.exit(1)

    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
