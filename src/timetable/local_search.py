"""Metaheurísticas de busca local: Tabu Search e Simulated Annealing.

Estas são as abordagens recomendadas pela literatura (ITC 2007, Wilke & Ostler 2008)
para o problema de horário escolar.

Operadores:
- Exchange (trocar slot de duas aulas) — movimento principal, mais comum que modify.
- Modify (mover uma aula para outro slot) — movimento secundário.

Respeita slots imutáveis do seed (horario.slots_imutaveis).

Performance: cada iteração chama `avaliar` (ou `avaliar_com_cache`) que recalcula
TODO o horário (O(n) sobre todas as aulas). Para instâncias grandes, isto pode
ser um gargalo. Veja `timetable.objective` para opções de cache e documentação
sobre avaliação incremental (ticket T016/F-006).
"""

from __future__ import annotations

import math
import random
import time
from collections import deque
from typing import Optional

from .constraints import ContextoRestricoes
from .models import Aula, Horario, Slot
from .objective import Avaliacao, avaliar, eh_melhor_que


# ---------------------------------------------------------------------------
# Operadores de movimento
# ---------------------------------------------------------------------------


def _gerar_vizinho_exchange(
    horario: Horario,
    _slots_disponiveis: list[Slot],
    rng: random.Random,
) -> tuple[Optional[Horario], Optional[tuple]]:
    """Gera um vizinho trocando os slots de duas aulas aleatórias.

    Não altera aulas cujos slots estejam em horario.slots_imutaveis.
    Retorna (vizinho, chave_tabu) ou (None, None) se não for possível.

    O parâmetro `slots_disponiveis` é mantido por compatibilidade com a
    assinatura de `_gerar_vizinho_modify`, mas não é usado aqui porque o
    exchange apenas troca slots entre aulas existentes.
    """

    vizinho = horario.clone()
    aulas_mutaveis = [a for a in vizinho.aulas if not vizinho.slot_e_imutavel(a.slot)]
    if len(aulas_mutaveis) < 2:
        return None, None

    a1, a2 = rng.sample(aulas_mutaveis, 2)
    slot1, slot2 = a1.slot, a2.slot

    # Troca os slots (preserva subgrupo_id)
    nova_a1 = Aula(a1.turma, a1.disciplina, a1.professor, a1.sala, slot2, subgrupo_id=a1.subgrupo_id)
    nova_a2 = Aula(a2.turma, a2.disciplina, a2.professor, a2.sala, slot1, subgrupo_id=a2.subgrupo_id)

    vizinho.remover(a1)
    vizinho.remover(a2)
    vizinho.adicionar(nova_a1)
    vizinho.adicionar(nova_a2)

    chave_tabu = _chave_tabu_exchange(a1, a2)
    return vizinho, chave_tabu


def _gerar_vizinho_modify(
    horario: Horario,
    slots_disponiveis: list[Slot],
    rng: random.Random,
) -> tuple[Optional[Horario], Optional[tuple]]:
    """Gera um vizinho movendo uma aula para outro slot aleatório.

    Não altera aulas cujos slots estejam em horario.slots_imutaveis.
    Retorna (vizinho, chave_tabu) ou (None, None) se não for possível.
    """

    vizinho = horario.clone()
    aulas_mutaveis = [a for a in vizinho.aulas if not vizinho.slot_e_imutavel(a.slot)]
    if not aulas_mutaveis or not slots_disponiveis:
        return None, None

    aula = rng.choice(aulas_mutaveis)
    novo_slot = rng.choice(slots_disponiveis)

    if novo_slot == aula.slot:
        return None, None

    nova_aula = Aula(
        turma=aula.turma,
        disciplina=aula.disciplina,
        professor=aula.professor,
        sala=aula.sala,
        slot=novo_slot,
        subgrupo_id=aula.subgrupo_id,
    )
    vizinho.remover(aula)
    vizinho.adicionar(nova_aula)

    chave_tabu = _chave_tabu_modify(aula, novo_slot)
    return vizinho, chave_tabu


# ---------------------------------------------------------------------------
# Chave de tabu
# ---------------------------------------------------------------------------


def _chave_tabu_exchange(a1: Aula, a2: Aula) -> tuple:
    """Chave canónica para um movimento de exchange."""

    slots = sorted([str(a1.slot), str(a2.slot)])
    turmas = sorted([a1.turma, a2.turma])
    disciplinas = sorted([a1.disciplina, a2.disciplina])
    return (
        "exchange",
        turmas[0],
        turmas[1],
        disciplinas[0],
        disciplinas[1],
        slots[0],
        slots[1],
    )


def _chave_tabu_modify(aula: Aula, novo_slot: Slot) -> tuple:
    """Chave canónica para um movimento de modify."""

    return ("modify", aula.turma, aula.disciplina, str(aula.slot), str(novo_slot))


# ---------------------------------------------------------------------------
# Simulated Annealing
# ---------------------------------------------------------------------------


def simulated_annealing(
    horario_inicial: Horario,
    ctx: ContextoRestricoes,
    slots: list[Slot],
    tempo_limite_segundos: float = 60.0,
    temperatura_inicial: float = 1000.0,
    resfriamento: float = 0.995,
    iteracoes_sem_melhoria_limite: int = 500,
    score_alvo: Optional[int] = None,
    semente: Optional[int] = None,
) -> Horario:
    """Simulated Annealing para horário escolar.

    Parâmetros:
    - tempo_limite_segundos: tempo máximo de execução.
    - temperatura_inicial: temperatura inicial do SA.
    - resfriamento: fator de resfriamento geométrico (0 < resfriamento < 1).
    - iteracoes_sem_melhoria_limite: parar se não houver melhoria após N iterações.
    - score_alvo: parar se atingir este score (satisficing).
    - semente: para reprodutibilidade.
    """

    if semente is not None:
        rng = random.Random(semente)
    else:
        rng = random.Random()

    inicio = time.time()
    atual = horario_inicial.clone()
    avaliacao_atual = avaliar(atual, ctx)
    melhor = atual.clone()
    avaliacao_melhor = avaliacao_atual

    temperatura = temperatura_inicial
    iteracoes_sem_melhoria = 0

    while (
        time.time() - inicio < tempo_limite_segundos
        and temperatura > 0.1
        and iteracoes_sem_melhoria < iteracoes_sem_melhoria_limite
    ):
        # Escolhe entre exchange (70%) e modify (30%)
        if rng.random() < 0.7:
            vizinho, _ = _gerar_vizinho_exchange(atual, slots, rng)
        else:
            vizinho, _ = _gerar_vizinho_modify(atual, slots, rng)

        if vizinho is None:
            break

        avaliacao_vizinho = avaliar(vizinho, ctx)
        delta = avaliacao_vizinho.score - avaliacao_atual.score

        if delta > 0 or rng.random() < math.exp(delta / temperatura):
            atual = vizinho
            avaliacao_atual = avaliacao_vizinho
            iteracoes_sem_melhoria = (
                0
                if eh_melhor_que(avaliacao_vizinho, avaliacao_melhor)
                else iteracoes_sem_melhoria + 1
            )

            if eh_melhor_que(avaliacao_vizinho, avaliacao_melhor):
                melhor = vizinho.clone()
                avaliacao_melhor = avaliacao_vizinho
        else:
            iteracoes_sem_melhoria += 1

        if score_alvo is not None and avaliacao_melhor.score >= score_alvo:
            break

        temperatura *= resfriamento

    return melhor


# ---------------------------------------------------------------------------
# Tabu Search
# ---------------------------------------------------------------------------


def tabu_search(
    horario_inicial: Horario,
    ctx: ContextoRestricoes,
    slots: list[Slot],
    tempo_limite_segundos: float = 60.0,
    tamanho_tabu: int = 50,
    iteracoes_sem_melhoria_limite: int = 500,
    score_alvo: Optional[int] = None,
    semente: Optional[int] = None,
    num_vizinhos: int = 30,
    proporcao_exchange: float = 0.7,
) -> Horario:
    """Tabu Search para horário escolar.

    Parâmetros:
    - tempo_limite_segundos: tempo máximo de execução.
    - tamanho_tabu: tamanho da lista tabu (FIFO).
    - iteracoes_sem_melhoria_limite: parar se não houver melhoria após N iterações.
    - score_alvo: parar se atingir este score (satisficing).
    - semente: para reprodutibilidade.
    - num_vizinhos: quantos vizinhos gerar e avaliar por iteração.
    - proporcao_exchange: fração de vizinhos que são exchange (0.0 a 1.0).
    """

    if semente is not None:
        rng = random.Random(semente)
    else:
        rng = random.Random()

    inicio = time.time()
    atual = horario_inicial.clone()
    avaliacao_atual = avaliar(atual, ctx)
    melhor = atual.clone()
    avaliacao_melhor = avaliacao_atual

    # FIFO com tamanho fixo; conjunto para consulta O(1)
    lista_tabu: deque[tuple] = deque(maxlen=tamanho_tabu)
    tabu_set: set[tuple] = set()
    iteracoes_sem_melhoria = 0

    while (
        time.time() - inicio < tempo_limite_segundos
        and iteracoes_sem_melhoria < iteracoes_sem_melhoria_limite
    ):
        vizinhos: list[tuple[Horario, Avaliacao, Optional[tuple]]] = []

        for _ in range(num_vizinhos):
            if rng.random() < proporcao_exchange:
                vizinho, chave_tabu = _gerar_vizinho_exchange(atual, slots, rng)
            else:
                vizinho, chave_tabu = _gerar_vizinho_modify(atual, slots, rng)

            if vizinho is None:
                continue

            avaliacao_vizinho = avaliar(vizinho, ctx)
            vizinhos.append((vizinho, avaliacao_vizinho, chave_tabu))

        if not vizinhos:
            break

        # Ordena por score descendente
        vizinhos.sort(key=lambda item: item[1].score, reverse=True)

        escolhido: Optional[tuple[Horario, Avaliacao]] = None
        chave_escolhida: Optional[tuple] = None

        for viz, av, chave in vizinhos:
            if chave is None:
                # Sem chave tabu (ex. modify inválido); aceita diretamente
                escolhido = (viz, av)
                chave_escolhida = None
                break

            if chave in tabu_set:
                # Critério de aspiração: aceita se melhora o global
                if eh_melhor_que(av, avaliacao_melhor):
                    escolhido = (viz, av)
                    chave_escolhida = chave
                    break
                continue

            escolhido = (viz, av)
            chave_escolhida = chave
            break

        if escolhido is None:
            break

        atual, avaliacao_atual = escolhido

        if chave_escolhida is not None:
            # Antes de adicionar, verifica se a deque vai estourar e remove o mais antigo do set
            if len(lista_tabu) == tamanho_tabu and tamanho_tabu > 0:
                chave_antiga = lista_tabu[0]  # será removida pelo append
                tabu_set.discard(chave_antiga)
            lista_tabu.append(chave_escolhida)
            tabu_set.add(chave_escolhida)

        if eh_melhor_que(avaliacao_atual, avaliacao_melhor):
            melhor = atual.clone()
            avaliacao_melhor = avaliacao_atual
            iteracoes_sem_melhoria = 0
        else:
            iteracoes_sem_melhoria += 1

        if score_alvo is not None and avaliacao_melhor.score >= score_alvo:
            break

    return melhor
