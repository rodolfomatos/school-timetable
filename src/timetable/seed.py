"""Geração de seed parcial imutável (~30% dos slots).

Estratégia recomendada na literatura: preencher uma fração dos slots com um
horário totalmente viável e mantê-lo imutável durante a busca, reduzindo
drasticamente o espaço de soluções.
"""

from __future__ import annotations

import random
from typing import Optional

from .models import Aula, Horario, Slot


def gerar_seed_parcial(
    horario: Horario,
    slots_disponiveis: list[Slot],
    taxa_preenchimento: float = 0.30,
    semente: Optional[int] = None,
) -> Horario:
    """Preenche aproximadamente `taxa_preenchimento` dos slots com aulas de seed.

    Esta é uma implementação de esqueleto: em produção, o preenchimento deve
    respeitar todas as restrições duras (ver T003/T004).
    """

    if semente is not None:
        random.seed(semente)

    slots_embaralhados = list(slots_disponiveis)
    random.shuffle(slots_embaralhados)

    num_alvo = max(1, int(len(slots_embaralhados) * taxa_preenchimento))
    preenchidos = 0

    for slot in slots_embaralhados:
        if preenchidos >= num_alvo:
            break
        aula = Aula(
            turma="Turma A",
            disciplina="Matemática",
            professor="Prof. X",
            sala="Sala 1",
            slot=slot,
        )
        horario.adicionar(aula)
        preenchidos += 1

    return horario


def marcar_como_imutavel(slots: list[Slot]) -> frozenset[Slot]:
    """Retorna os slots do seed como um conjunto imutável."""

    return frozenset(slots)
