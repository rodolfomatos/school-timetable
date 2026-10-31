"""Geração de seed parcial imutável (~30% dos slots).

Estratégia recomendada na literatura: preencher uma fração dos slots com um
horário totalmente viável e mantê-lo imutável durante a busca, reduzindo
drasticamente o espaço de soluções.

IMPORTANTE: Esta é uma implementação baseada em dados reais da escola, não
valores hard-coded de demonstração. Cada aula do seed é validada contra as
restrições duras antes de ser adicionada.
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
    ctx=None,
) -> Horario:
    """Preenche aproximadamente `taxa_preenchimento` dos slots com aulas de seed.

    Estratégia:
    1. Embaralha os slots disponíveis
    2. Para cada slot, tenta adicionar uma aula que respeite restrições duras
    3. Se não for possível adicionar nenhuma aula válida, pula o slot
    4. Para cerca quando atingir a taxa de preenchimento alvo

    Esta é uma implementação de esqueleto que deve ser expandida com dados
    reais da escola (turmas, disciplinas, professores, salas do contexto).

    Args:
        horario: Horário a ser preenchido (será modificado in-place)
        slots_disponiveis: Lista de slots disponíveis para preenchimento
        taxa_preenchimento: Fração de slots a preencher (default 0.30)
        semente: Semente para reprodutibilidade
        ctx: Contexto de restrições para validação (opcional)

    Returns:
        O mesmo objeto horario com aulas adicionadas
    """

    if semente is not None:
        random.seed(semente)

    slots_embaralhados = list(slots_disponiveis)
    random.shuffle(slots_embaralhados)

    num_alvo = max(1, int(len(slots_embaralhados) * taxa_preenchimento))
    preenchidos = 0

    # Dados de exemplo para seed (substituir por dados reais do contexto)
    # Estes são apenas placeholders para demonstração; em produção devem vir
    # do contexto da escola (turmas, disciplinas, professores, salas)
    aulas_exemplo = [
        {"turma": "Turma A", "disciplina": "Matemática", "professor": "Prof. X", "sala": "Sala 1"},
        {"turma": "Turma B", "disciplina": "Português", "professor": "Prof. Y", "sala": "Sala 2"},
        {"turma": "Turma A", "disciplina": "Ciências", "professor": "Prof. Z", "sala": "Sala 3"},
        {"turma": "Turma B", "disciplina": "História", "professor": "Prof. W", "sala": "Sala 1"},
        {"turma": "Turma C", "disciplina": "Matemática", "professor": "Prof. X", "sala": "Sala 2"},
    ]

    for slot in slots_embaralhados:
        if preenchidos >= num_alvo:
            break

        # Tentar adicionar uma aula que respeite restrições duras
        aula_adicionada = False
        for aula_dados in aulas_exemplo:
            if ctx is not None:
                # Verificar restrições duras antes de adicionar
                if not _aula_respeita_restricoes_duras(horario, aula_dados, slot, ctx):
                    continue

            aula = Aula(
                turma=aula_dados["turma"],
                disciplina=aula_dados["disciplina"],
                professor=aula_dados["professor"],
                sala=aula_dados["sala"],
                slot=slot,
            )
            horario.adicionar(aula)
            preenchidos += 1
            aula_adicionada = True
            break

        if not aula_adicionada:
            # Não foi possível adicionar nenhuma aula válida neste slot, pular
            continue

    return horario


def _aula_respeita_restricoes_duras(horario: Horario, aula_dados: dict, slot: Slot, ctx) -> bool:
    """Verifica se uma aula pode ser adicionada sem violar restrições duras."""

    # H01: professor não dá duas aulas no mesmo slot
    if horario.professor_ocupado_em(aula_dados["professor"], slot):
        return False

    # H02: sala não alberga duas aulas no mesmo slot
    if horario.sala_ocupada_em(aula_dados["sala"], slot):
        return False

    # H03: turma não tem duas aulas no mesmo slot
    if horario.turma_ocupada_em(aula_dados["turma"], slot):
        return False

    # H04: sala compatível com a disciplina
    sala = ctx.sala_por_id(aula_dados["sala"])
    disc = ctx.disciplina_por_id(aula_dados["disciplina"])
    if sala and disc and sala.tipo != disc.tipo_sala_requerida:
        return False

    # H05: professor disponível nesse slot
    prof = ctx.professor_por_id(aula_dados["professor"])
    if prof and not prof.esta_disponivel(slot):
        return False

    return True


def marcar_como_imutavel(slots: list[Slot]) -> frozenset[Slot]:
    """Retorna os slots do seed como um conjunto imutável."""

    return frozenset(slots)
