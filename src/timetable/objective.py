"""Função objetivo aditiva para o problema de horário escolar.

Princípio: soma de penalidades pelas restrições moles quebradas.
Nunca usar produto multiplicativo de pesos (problema reportado na literatura:
números astronómicos, necessidade de bignum, perda de granularidade).

Cache: 
- `avaliar_com_cache` usa chave composta por (horario_fingerprint, contexto_fingerprint).
- Contexto fingerprint inclui hash dos dados que afetam a avaliação.
- Tamanho do cache limitado (LRU) e observável.

Avaliação incremental:
- `avaliar_incremental` aceita delta de aulas (removidas/adicionadas).
- Recalcula apenas penalidades afetadas pelas aulas alteradas.
- Útil para metaheurísticas que fazem movimentos locais.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from .constraints import ContextoRestricoes, calcular_penalidades_moles, verificar_hard
from .models import Aula, Horario

MUITO_NEGATIVO = -1_000_000

# Cache LRU com tamanho máximo
_MAX_CACHE_SIZE = 10_000
_cache_avaliacao: "OrderedDict[tuple, Avaliacao]" = OrderedDict()
_cache_stats = {"hits": 0, "misses": 0, "evictions": 0}


def _fingerprint_horario(horario: Horario) -> str:
    """Gera fingerprint SHA256 do horário (aulas ordenadas)."""
    data = tuple(
        sorted(
            (a.turma, a.disciplina, a.professor, a.sala, a.slot.dia, a.slot.hora, a.subgrupo_id or "")
            for a in horario.aulas
        )
    )
    return sha256(repr(data).encode()).hexdigest()[:16]


def _fingerprint_contexto(ctx: ContextoRestricoes) -> str:
    """Gera fingerprint SHA256 do contexto (dados que afetam avaliação)."""
    # Professores: disponibilidade, dia_folga, prefere_manha, cargas, qualificações
    prof_data = tuple(
        sorted(
            (
                pid,
                tuple(sorted(p.disponibilidade)),
                p.dia_folga_preferido or "",
                p.prefere_manha,
                p.carga_maxima_semanal,
                p.carga_minima_semanal,
                tuple(sorted(p.qualificacoes)),
            )
            for pid, p in ctx.professores.items()
        )
    )
    # Salas: tipo, capacidade
    sala_data = tuple(
        sorted((sid, s.tipo, s.capacidade) for sid, s in ctx.salas.items())
    )
    # Disciplinas: carga_semanal, tipo_sala_requerida
    disc_data = tuple(
        sorted((did, d.carga_semanal, d.tipo_sala_requerida) for did, d in ctx.disciplinas.items())
    )
    # Casamentos e relações filho
    casamentos_data = tuple(sorted((c.professor_a, c.professor_b) for c in ctx.casamentos))
    relacoes_data = tuple(
        sorted((r.professor_pai, r.professor_mae, r.identificador_turma_filho) for r in ctx.relacoes_filho)
    )
    # Subgrupos
    subgrupos_data = tuple(
        sorted((sid, s.turma_pai, s.numero_alunos) for sid, s in ctx.subgrupos.items())
    )

    combined = (
        prof_data,
        sala_data,
        disc_data,
        casamentos_data,
        relacoes_data,
        subgrupos_data,
    )
    return sha256(repr(combined).encode()).hexdigest()[:16]


def _chave_composta(horario: Horario, ctx: ContextoRestricoes) -> tuple[str, str]:
    """Chave composta: (fingerprint_horario, fingerprint_contexto)."""
    return (_fingerprint_horario(horario), _fingerprint_contexto(ctx))


def avaliar_com_cache(
    horario: Horario,
    ctx: ContextoRestricoes,
) -> "Avaliacao":
    """Avalia um horário usando cache LRU com chave composta (horario + contexto).

    Se o mesmo horário no mesmo contexto já foi avaliado, devolve o
    resultado em cache. Caso contrário, avalia e armazena no cache.
    """
    global _cache_stats

    chave = _chave_composta(horario, ctx)
    if chave in _cache_avaliacao:
        _cache_stats["hits"] += 1
        # Move to end (LRU)
        _cache_avaliacao.move_to_end(chave)
        return _cache_avaliacao[chave]

    _cache_stats["misses"] += 1
    resultado = avaliar(horario, ctx)

    # LRU eviction
    if len(_cache_avaliacao) >= _MAX_CACHE_SIZE:
        _cache_avaliacao.popitem(last=False)
        _cache_stats["evictions"] += 1

    _cache_avaliacao[chave] = resultado
    return resultado


def avaliar_incremental(
    horario_base: Horario,
    ctx: ContextoRestricoes,
    aulas_removidas: list[Aula],
    aulas_adicionadas: list[Aula],
    avaliacao_base: Optional["Avaliacao"] = None,
) -> "Avaliacao":
    """Avaliação incremental: recalcula apenas o afetado pelas aulas alteradas.

    Args:
        horario_base: Horário antes do movimento.
        ctx: Contexto de restrições.
        aulas_removidas: Aulas que foram removidas (ex: movidas de slot).
        aulas_adicionadas: Aulas que foram adicionadas (ex: no novo slot).
        avaliacao_base: Avaliação prévia do horario_base (se None, calcula).

    Returns:
        Nova avaliação do horário resultante.

    Nota: Se o movimento causar violações duras nas aulas não alteradas
    (impossível em movimentos válidos), a avaliação completa é feita.
    """
    # Se não há avaliação base, faz completa
    if avaliacao_base is None:
        return avaliar(horario_base, ctx)

    # Se base já inviável, qualquer movimento mantém inviável
    if not avaliacao_base.viavel:
        return avaliar(horario_base, ctx)

    # Identificar entidades afetadas
    professores_afetados = set()
    salas_afetadas = set()
    turmas_afetadas = set()
    disciplinas_afetadas = set()
    subgrupos_afetados = set()
    dias_afetados = set()

    for a in aulas_removidas + aulas_adicionadas:
        professores_afetados.add(a.professor)
        salas_afetadas.add(a.sala)
        turmas_afetadas.add(a.turma)
        disciplinas_afetadas.add(a.disciplina)
        if a.subgrupo_id:
            subgrupos_afetados.add(a.subgrupo_id)
        dias_afetados.add(a.slot.dia)

    # Verificar hard constraints apenas nas entidades afetadas
    violacoes = _verificar_hard_incremental(
        horario_base, ctx, aulas_removidas, aulas_adicionadas,
        professores_afetados, salas_afetadas, turmas_afetadas,
        disciplinas_afetadas, subgrupos_afetados, dias_afetados
    )

    if violacoes:
        return avaliar(horario_base, ctx)

    # Recalcular penalidades moles apenas para entidades afetadas
    delta_penalidades = _calcular_delta_penalidades_moles(
        horario_base, ctx, aulas_removidas, aulas_adicionadas,
        professores_afetados, salas_afetadas, turmas_afetadas,
        disciplinas_afetadas, subgrupos_afetados, dias_afetados
    )

    # score = -penalidades_moles, então novo_score = -novas_penalidades
    novas_penalidades = avaliacao_base.penalidades_moles + delta_penalidades
    novo_score = -novas_penalidades

    return Avaliacao(
        viavel=True,
        violacoes_hard=[],
        penalidades_moles=novas_penalidades,
        score=novo_score,
    )


def _verificar_hard_incremental(
    horario: Horario,
    ctx: ContextoRestricoes,
    aulas_removidas: list[Aula],
    aulas_adicionadas: list[Aula],
    professores: set[str],
    salas: set[str],
    turmas: set[str],
    disciplinas: set[str],
    subgrupos: set[str],
    dias: set[str],
) -> list[str]:
    """Verifica hard constraints apenas nas entidades afetadas."""
    violacoes = []

    # H01: professor não dá duas aulas no mesmo slot
    for prof in professores:
        for slot in (a.slot for a in aulas_adicionadas if a.professor == prof):
            count = sum(1 for a in horario.aulas if a.professor == prof and a.slot == slot)
            count += sum(1 for a in aulas_adicionadas if a.professor == prof and a.slot == slot)
            count -= sum(1 for a in aulas_removidas if a.professor == prof and a.slot == slot)
            if count > 1:
                violacoes.append(f"H01: professor {prof} em {slot} em {count} aulas")

    # H02: sala não alberga duas aulas no mesmo slot
    for sala in salas:
        for slot in (a.slot for a in aulas_adicionadas if a.sala == sala):
            count = sum(1 for a in horario.aulas if a.sala == sala and a.slot == slot)
            count += sum(1 for a in aulas_adicionadas if a.sala == sala and a.slot == slot)
            count -= sum(1 for a in aulas_removidas if a.sala == sala and a.slot == slot)
            if count > 1:
                violacoes.append(f"H02: sala {sala} em {slot} com {count} aulas")

    # H03: turma+subgrupo não tem duas aulas no mesmo slot
    for turma in turmas:
        for slot in (a.slot for a in aulas_adicionadas if a.turma == turma):
            for sub_id in (None, *subgrupos):
                count = sum(
                    1 for a in horario.aulas
                    if a.turma == turma and a.slot == slot and a.subgrupo_id == sub_id
                )
                count += sum(
                    1 for a in aulas_adicionadas
                    if a.turma == turma and a.slot == slot and a.subgrupo_id == sub_id
                )
                count -= sum(
                    1 for a in aulas_removidas
                    if a.turma == turma and a.slot == slot and a.subgrupo_id == sub_id
                )
                if count > 1:
                    sub_str = sub_id if sub_id else "turma_inteira"
                    violacoes.append(f"H03: turma {turma} (subgrupo {sub_str}) em {slot} com {count} aulas")

    # H04: sala compatível com a disciplina
    for a in aulas_adicionadas:
        sala = ctx.sala_por_id(a.sala)
        disc = ctx.disciplina_por_id(a.disciplina)
        if sala and disc and sala.tipo != disc.tipo_sala_requerida:
            violacoes.append(f"H04: sala {a.sala} ({sala.tipo}) não serve {a.disciplina} ({disc.tipo_sala_requerida})")

    # H05: professor disponível nesse slot
    for a in aulas_adicionadas:
        prof = ctx.professor_por_id(a.professor)
        if prof and not prof.esta_disponivel(a.slot):
            violacoes.append(f"H05: professor {a.professor} não disponível em {a.slot}")

    # H07: professores casados não na mesma turma
    casados = {(c.professor_a, c.professor_b) for c in ctx.casamentos} | {
        (c.professor_b, c.professor_a) for c in ctx.casamentos
    }
    for a in aulas_adicionadas:
        for pa, pb in casados:
            if a.professor == pa:
                # Verificar se cônjuge está na mesma turma+slot+subgrupo
                conflito = any(
                    a2.turma == a.turma and a2.slot == a.slot and a2.subgrupo_id == a.subgrupo_id
                    for a2 in horario.aulas + aulas_adicionadas
                    if a2.professor == pb
                )
                if conflito:
                    violacoes.append(f"H07: professores casados {pa} e {pb} na turma {a.turma} em {a.slot}")

    # H08: filho não na turma dos pais casados
    for rel in ctx.relacoes_filho:
        for a in aulas_adicionadas:
            if a.turma == rel.identificador_turma_filho and a.professor in (rel.professor_pai, rel.professor_mae):
                violacoes.append(f"H08: {a.professor} leciona na turma do filho {rel.identificador_turma_filho}")

    return violacoes


def _calcular_delta_penalidades_moles(
    horario: Horario,
    ctx: ContextoRestricoes,
    aulas_removidas: list[Aula],
    aulas_adicionadas: list[Aula],
    professores: set[str],
    salas: set[str],
    turmas: set[str],
    disciplinas: set[str],
    subgrupos: set[str],
    dias: set[str],
) -> int:
    """Calcula a diferença de penalidades moles (novo - antigo).

    Estratégia: para cada restrição, calcula a penalidade no estado "base" (horario)
    e no estado "novo" (horario - removidas + adicionadas), e retorna a diferença.
    """
    # Construir estado novo
    aulas_novas = [a for a in horario.aulas if a not in aulas_removidas] + aulas_adicionadas

    delta = 0

    # S01: dia de folga preferido
    def _s01(aulas: list[Aula]) -> int:
        return sum(
            10
            for a in aulas
            if (prof := ctx.professor_por_id(a.professor))
            and prof.dia_folga_preferido
            and a.slot.dia == prof.dia_folga_preferido
        )

    # S02: preferência manhã/tarde
    def _s02(aulas: list[Aula]) -> int:
        return sum(
            8
            for a in aulas
            if (prof := ctx.professor_por_id(a.professor))
            and prof.prefere_manha
            and a.slot.hora >= 13
        )

    # S03: duas horas consecutivas (mesma disciplina, mesma turma)
    def _s03(aulas: list[Aula]) -> int:
        penalidade = 0
        aulas_por_turma_disc: dict[tuple[str, str], list[Aula]] = {}
        for a in aulas:
            chave = (a.turma, a.disciplina)
            aulas_por_turma_disc.setdefault(chave, []).append(a)
        for (turm, disc), aulas in aulas_por_turma_disc.items():
            if len(aulas) < 2:
                continue
            slots_ordenados = sorted([(a.slot.dia, a.slot.hora) for a in aulas])
            tem_consecutivas = any(
                slots_ordenados[i][0] == slots_ordenados[i + 1][0]
                and slots_ordenados[i][1] + 1 == slots_ordenados[i + 1][1]
                for i in range(len(slots_ordenados) - 1)
            )
            if not tem_consecutivas:
                penalidade += 6
        return penalidade

    # S04: disciplinas não espalhadas pela semana
    def _s04(aulas: list[Aula]) -> int:
        penalidade = 0
        aulas_por_turma_disc_dia: dict[tuple[str, str, str], list[Aula]] = {}
        for a in aulas:
            chave = (a.turma, a.disciplina, a.slot.dia)
            aulas_por_turma_disc_dia.setdefault(chave, []).append(a)
        disciplinas_por_turma_dia: dict[tuple[str, str], set[str]] = {}
        for (turm, disc, dia), aulas_dia in aulas_por_turma_disc_dia.items():
            disciplinas_por_turma_dia.setdefault((turm, disc), set()).add(dia)
        for (turm, disc), dias in disciplinas_por_turma_dia.items():
            if (
                len(dias) == 1
                and sum(len(aulas_por_turma_disc_dia.get((turm, disc, d), [])) for d in dias) >= 2
            ):
                penalidade += 5
        return penalidade

    # S05: padrão A-B-C-A
    def _s05(aulas: list[Aula]) -> int:
        penalidade = 0
        aulas_por_turma_dia: dict[tuple[str, str], list[tuple[int, str]]] = {}
        for a in aulas:
            chave = (a.turma, a.slot.dia)
            aulas_por_turma_dia.setdefault(chave, []).append((a.slot.hora, a.disciplina))
        for (turm, dia), aulas_hora_disc in aulas_por_turma_dia.items():
            aulas_hora_disc.sort()
            disciplinas_ordenadas = [disc for _, disc in aulas_hora_disc]
            for i in range(len(disciplinas_ordenadas) - 3):
                if (
                    disciplinas_ordenadas[i] == disciplinas_ordenadas[i + 3]
                    and disciplinas_ordenadas[i] != disciplinas_ordenadas[i + 1]
                    and disciplinas_ordenadas[i] != disciplinas_ordenadas[i + 2]
                    and disciplinas_ordenadas[i + 1] != disciplinas_ordenadas[i + 2]
                ):
                    penalidade += 7
                    break
        return penalidade

    # S06: falta de duas horas consecutivas para avaliação
    def _s06(aulas: list[Aula]) -> int:
        penalidade = 0
        aulas_por_prof_dia: dict[tuple[str, str], list[int]] = {}
        for a in aulas:
            prof = ctx.professor_por_id(a.professor)
            if prof and prof.carga_maxima_semanal >= 4:
                chave = (a.professor, a.slot.dia)
                aulas_por_prof_dia.setdefault(chave, []).append(a.slot.hora)
        for (prof_id, dia), horas in aulas_por_prof_dia.items():
            horas.sort()
            tem_bloco_consecutivo = any(horas[i] + 1 == horas[i + 1] for i in range(len(horas) - 1))
            if not tem_bloco_consecutivo and len(horas) >= 2:
                penalidade += 9
        return penalidade

    # S07: carga horária do professor fora dos limites
    def _s07(aulas: list[Aula]) -> int:
        penalidade = 0
        aulas_por_prof: dict[str, list[Aula]] = {}
        for a in aulas:
            aulas_por_prof.setdefault(a.professor, []).append(a)
        for prof_id, aulas_prof in aulas_por_prof.items():
            prof = ctx.professor_por_id(prof_id)
            if prof:
                total_aulas = len(aulas_prof)
                if total_aulas < prof.carga_minima_semanal or total_aulas > prof.carga_maxima_semanal:
                    penalidade += 8
        return penalidade

    # S08: professor a trabalhar muitos dias seguidos
    def _s08(aulas: list[Aula]) -> int:
        penalidade = 0
        aulas_por_prof: dict[str, list[Aula]] = {}
        for a in aulas:
            aulas_por_prof.setdefault(a.professor, []).append(a)
        for prof_id, aulas_prof in aulas_por_prof.items():
            dias_com_aula = {a.slot.dia for a in aulas_prof}
            if len(dias_com_aula) >= 5:
                penalidade += 12
        return penalidade

    # S09: distribuição desigual entre professores da mesma disciplina
    def _s09(aulas: list[Aula]) -> int:
        penalidade = 0
        aulas_por_disc_prof: dict[tuple[str, str], int] = {}
        for a in aulas:
            chave = (a.disciplina, a.professor)
            aulas_por_disc_prof[chave] = aulas_por_disc_prof.get(chave, 0) + 1
        disciplinas_professores: dict[str, list[int]] = {}
        for (disc, prof_id), count in aulas_por_disc_prof.items():
            disciplinas_professores.setdefault(disc, []).append(count)
        for disc, contagens in disciplinas_professores.items():
            if len(contagens) > 1:
                diferenca = max(contagens) - min(contagens)
                if diferenca > 2:
                    penalidade += 11
        return penalidade

    # S10: carga concentrada em poucos dias
    def _s10(aulas: list[Aula]) -> int:
        penalidade = 0
        aulas_por_prof: dict[str, list[Aula]] = {}
        for a in aulas:
            aulas_por_prof.setdefault(a.professor, []).append(a)
        for prof_id, aulas_prof in aulas_por_prof.items():
            dias_com_aula = {a.slot.dia for a in aulas_prof}
            if len(dias_com_aula) <= 2 and len(aulas_prof) >= 5:
                penalidade += 10
        return penalidade

    # Calcular delta para cada restrição
    for fn in [_s01, _s02, _s03, _s04, _s05, _s06, _s07, _s08, _s09, _s10]:
        delta += fn(aulas_novas) - fn(horario.aulas)

    return delta


def limpar_cache_avaliacao() -> None:
    """Limpa o cache de avaliação. Útil entre execuções independentes."""
    global _cache_stats
    _cache_avaliacao.clear()
    _cache_stats = {"hits": 0, "misses": 0, "evictions": 0}


def estatisticas_cache() -> dict:
    """Retorna estatísticas do cache."""
    return {
        "size": len(_cache_avaliacao),
        "max_size": _MAX_CACHE_SIZE,
        "hits": _cache_stats["hits"],
        "misses": _cache_stats["misses"],
        "evictions": _cache_stats["evictions"],
        "hit_rate": _cache_stats["hits"] / max(1, _cache_stats["hits"] + _cache_stats["misses"]),
    }


@dataclass(frozen=True)
class Avaliacao:
    """Resultado da avaliação de um horário."""

    viavel: bool
    violacoes_hard: list[str]
    penalidades_moles: int
    score: int  # quanto maior (menos negativo), melhor


def avaliar(
    horario: Horario,
    ctx: ContextoRestricoes,
) -> Avaliacao:
    """Avalia um horário completo.

    Regras:
    - Se houver violações duras, o score é -infinito (representado por um inteiro muito negativo).
    - Caso contrário, score = - soma das penalidades moles.
    """

    violacoes = verificar_hard(horario, ctx)
    penalidades = calcular_penalidades_moles(horario, ctx)
    soma_penalidades = sum(p.valor for p in penalidades)

    if violacoes:
        return Avaliacao(
            viavel=False,
            violacoes_hard=violacoes,
            penalidades_moles=soma_penalidades,
            score=MUITO_NEGATIVO - soma_penalidades,
        )

    return Avaliacao(
        viavel=True,
        violacoes_hard=[],
        penalidades_moles=soma_penalidades,
        score=-soma_penalidades,
    )


def eh_melhor_que(novo: Avaliacao, anterior: Avaliacao) -> bool:
    """Compara duas avaliações. Maior score é melhor."""

    return novo.score > anterior.score