"""Função objetivo aditiva para o problema de horário escolar.

Princípio: soma de penalidades pelas restrições moles quebradas.
Nunca usar produto multiplicativo de pesos (problema reportado na literatura:
números astronómicos, necessidade de bignum, perda de granularidade).

Performance: cada chamada a `avaliar` recalcula TODO o horário (O(n) sobre
todas as aulas). Para instâncias grandes (centenas de aulas), isto pode ser um
gargalo nas metaheurísticas. Uma otimização simples é o cache de avaliação
(`avaliar_com_cache`), que evita recalcular horários já vistos. Para avaliação
verdadeiramente incremental (recalcular apenas as penalidades afetadas por um
movimento), seria necessário refatorar `calcular_penalidades_moles` e
`verificar_hard` para aceitar deltas — veja ticket T016/F-006.
"""

from __future__ import annotations

from dataclasses import dataclass

from .constraints import ContextoRestricoes, calcular_penalidades_moles, verificar_hard
from .models import Horario

MUITO_NEGATIVO = -1_000_000

# Cache de avaliação: chave = representação hashável do horário, valor = Avaliacao
_cache_avaliacao: dict[tuple, Avaliacao] = {}


def _chave_horario(horario: Horario) -> tuple:
    """Gera uma chave hashável para um horário, baseada nas suas aulas ordenadas."""

    return tuple(
        sorted(
            (a.turma, a.disciplina, a.professor, a.sala, a.slot.dia, a.slot.hora)
            for a in horario.aulas
        )
    )


def avaliar_com_cache(
    horario: Horario,
    ctx: ContextoRestricoes,
) -> Avaliacao:
    """Avalia um horário usando cache para evitar recálculos desnecessários.

    Se o mesmo horário (mesmo conjunto de aulas) já foi avaliado, devolve o
    resultado em cache. Caso contrário, avalia e armazena no cache.
    """

    chave = _chave_horario(horario)
    if chave in _cache_avaliacao:
        return _cache_avaliacao[chave]

    resultado = avaliar(horario, ctx)
    _cache_avaliacao[chave] = resultado
    return resultado


def limpar_cache_avaliacao() -> None:
    """Limpa o cache de avaliação. Útil entre execuções independentes."""

    _cache_avaliacao.clear()


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
