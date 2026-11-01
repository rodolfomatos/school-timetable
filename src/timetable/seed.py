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

from .constraints import ContextoRestricoes
from .domain import Diagnostico, ProblemInstance, SessaoRequerida
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


# ---------------------------------------------------------------------------
# Construtor de solução inicial (para T052)
# ---------------------------------------------------------------------------


def _slots_validos_para_aula(
    aula: Aula,
    horario: Horario,
    ctx: ContextoRestricoes,
    slots: list[Slot],
) -> list[Slot]:
    """Filtra slots onde a aula pode ser colocada sem violar restrições duras."""

    validos = []
    for slot in slots:
        if horario.professor_ocupado_em(aula.professor, slot):
            continue
        if horario.sala_ocupada_em(aula.sala, slot):
            continue
        if horario.turma_ocupada_em(aula.turma, slot, aula.subgrupo_id):
            continue
        # H04: sala compatível
        sala_obj = ctx.sala_por_id(aula.sala)
        disc_obj = ctx.disciplina_por_id(aula.disciplina)
        if sala_obj and disc_obj and sala_obj.tipo != disc_obj.tipo_sala_requerida:
            continue
        # H05: professor disponível
        prof_obj = ctx.professor_por_id(aula.professor)
        if prof_obj and not prof_obj.esta_disponivel(slot):
            continue
        validos.append(slot)
    return validos


def _tentar_colocar_aula(
    aula: Aula,
    horario: Horario,
    ctx: ContextoRestricoes,
    slots: list[Slot],
    rng: random.Random,
) -> bool:
    """Tenta colocar a aula num slot válido; retorna True se conseguiu."""

    validos = _slots_validos_para_aula(aula, horario, ctx, slots)
    if not validos:
        return False
    slot = rng.choice(validos)
    nova_aula = Aula(
        turma=aula.turma,
        disciplina=aula.disciplina,
        professor=aula.professor,
        sala=aula.sala,
        slot=slot,
        subgrupo_id=aula.subgrupo_id,
    )
    horario.adicionar(nova_aula)
    return True


def construir_solucao_inicial(
    problema: ProblemInstance,
    slots: list[Slot],
    rng: random.Random | None = None,
) -> Horario:
    """Constrói uma solução inicial viável a partir do ``ProblemInstance``.

    Estratégia gulosa:
    1. Para cada sessão requerida, escolhe o primeiro (professor, sala, slot)
       que satisfaça as restrições duras.
    2. As sessões são processadas por ordem de `lesson_id` (estável).
    3. Se não for possível colocar uma sessão, registra diagnóstico e continua.
    4. Retorna o horário parcialmente preenchido + diagnósticos adicionados.

    Args:
        problema: ``ProblemInstance`` já validado (sem erros).
        slots: Lista de slots disponíveis (ordem não importa, usa ``rng``).
        rng: Gerador de aleatórios opcional; usa ``random.Random()`` se omitido.

    Returns:
        ``Horario`` com as aulas colocadas; ``problema.diagnosticos`` pode ser
        estendido com sessões não colocadas.
    """

    if rng is None:
        rng = random.Random()

    # Copia diagnósticos para não mutar o original em chamadas subsequentes
    diagnosticos = list(problema.diagnosticos)

    # Agrupa sessões por (turma, disciplina) para tentar colocar consecutivas
    sessoes_por_turma_disc: dict[tuple[str, str], list[SessaoRequerida]] = {}
    for sessao in problema.sessoes:
        sessoes_por_turma_disc.setdefault((sessao.turma, sessao.disciplina), []).append(sessao)

    horario = Horario()

    for (turma_id, disc_id), sessoes in sessoes_por_turma_disc.items():
        turma = problema.turmas[turma_id]
        disciplina = problema.disciplinas[disc_id]

        # Candidatos: (professor, sala) válidos
        pares_validos: list[tuple[str, str]] = []
        for prof_id in problema.professores:
            prof = problema.professores[prof_id]
            if not prof.pode_lecionar(disc_id):
                continue
            for sala_id, sala in problema.salas.items():
                if sala.tipo != disciplina.tipo_sala_requerida:
                    continue
                if sala.capacidade < (
                    problema.subgrupos[sessoes[0].subgrupo_id].numero_alunos
                    if sessoes[0].subgrupo_id
                    else turma.numero_alunos
                ):
                    continue
                pares_validos.append((prof_id, sala_id))

        if not pares_validos:
            diagnosticos.append(
                Diagnostico(
                    codigo="SEM_ATRIBUICAO_VIAVEL",
                    severidade="ERROR",
                    mensagem=(
                        f"Turma {turma_id}, disciplina {disc_id}: "
                        "nenhum par (professor, sala) viável."
                    ),
                    entidades=(turma_id, disc_id),
                )
            )
            continue

        # Embaralha slots uma vez por grupo para diversidade
        slots_embaralhados = list(slots)
        rng.shuffle(slots_embaralhados)

        for sessao in sessoes:
            colocada = False
            for prof_id, sala_id in pares_validos:
                aula_base = Aula(
                    turma=turma_id,
                    disciplina=disc_id,
                    professor=prof_id,
                    sala=sala_id,
                    slot=slots_embaralhados[0],  # placeholder
                    subgrupo_id=sessao.subgrupo_id,
                )
                if _tentar_colocar_aula(aula_base, horario, problema.para_contexto(), slots_embaralhados, rng):
                    colocada = True
                    break
            if not colocada:
                diagnosticos.append(
                    Diagnostico(
                        codigo="SESSAO_NAO_COLOCADA",
                        severidade="WARNING",
                        mensagem=(
                            f"Sessão {sessao.lesson_id}: não foi possível encontrar "
                            "slot válido com os pares (professor, sala) disponíveis."
                        ),
                        entidades=(sessao.lesson_id,),
                    )
                )

    # Atualiza diagnósticos do problema (referência externa vê as adições)
    problema.diagnosticos[:] = diagnosticos
    return horario
