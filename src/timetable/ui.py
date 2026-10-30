"""Interface de ajustamento manual ("insets de plástico").

Permite ao utilizador visualizar e editar o horário como uma grade, com
respeito a slots imutáveis (seed) e validação de restrições duras após cada
movimento.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constraints import ContextoRestricoes, verificar_hard
from .models import Aula, Horario, Slot


def exportar_json(horario: Horario, caminho: str | Path) -> None:
    """Exporta o horário para JSON."""

    dados: dict[str, Any] = {
        "versao": "0.1",
        "aulas": [
            {
                "turma": a.turma,
                "disciplina": a.disciplina,
                "professor": a.professor,
                "sala": a.sala,
                "slot": {"dia": a.slot.dia, "hora": a.slot.hora},
            }
            for a in horario.aulas
        ],
        "slots_imutaveis": [{"dia": s.dia, "hora": s.hora} for s in horario.slots_imutaveis],
    }
    Path(caminho).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


_CAMPOS_OBRIGATORIOS_AULA = ("turma", "disciplina", "professor", "sala", "slot")
_CAMPOS_OBRIGATORIOS_SLOT = ("dia", "hora")


def _validar_estrutura_json(dados: dict) -> None:
    """Valida a estrutura obrigatória do JSON de horário.

    Levanta ValueError com mensagem descritiva se campos obrigatórios estiverem
    em falta.
    """

    if "aulas" not in dados:
        raise ValueError("JSON de horário: campo 'aulas' em falta")

    for i, item in enumerate(dados["aulas"]):
        for campo in _CAMPOS_OBRIGATORIOS_AULA:
            if campo not in item:
                raise ValueError(f"JSON de horário: aula[{i}] campo '{campo}' em falta")
        if "slot" in item:
            for campo in _CAMPOS_OBRIGATORIOS_SLOT:
                if campo not in item["slot"]:
                    raise ValueError(f"JSON de horário: aula[{i}] slot.campo '{campo}' em falta")


def importar_json(caminho: str | Path) -> Horario:
    """Importa um horário de JSON."""

    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    _validar_estrutura_json(dados)
    aulas = [
        Aula(
            turma=item["turma"],
            disciplina=item["disciplina"],
            professor=item["professor"],
            sala=item["sala"],
            slot=Slot(dia=item["slot"]["dia"], hora=item["slot"]["hora"]),
        )
        for item in dados.get("aulas", [])
    ]
    imutaveis = frozenset(
        Slot(dia=s["dia"], hora=s["hora"]) for s in dados.get("slots_imutaveis", [])
    )
    return Horario(aulas=aulas, slots_imutaveis=imutaveis)


def gerar_grade(horario: Horario) -> dict[tuple[str, Slot], Aula]:
    """Converte um Horario em uma grade indexada por (turma, slot).

    Útil para visualização em estilo "tabela com insets de plástico".
    """

    grade: dict[tuple[str, Slot], Aula] = {}
    for aula in horario.aulas:
        grade[(aula.turma, aula.slot)] = aula
    return grade


def _aula_por_slot(horario: Horario, turma: str, slot: Slot) -> Aula | None:
    """Retorna a aula de uma turma num slot específico, se existir."""

    for aula in horario.aulas:
        if aula.turma == turma and aula.slot == slot:
            return aula
    return None


def _slot_e_imutavel(horario: Horario, slot: Slot) -> bool:
    """Verifica se um slot está no conjunto de slots imutáveis."""

    return slot in horario.slots_imutaveis


def mover_aula(
    horario: Horario,
    aula: Aula,
    novo_slot: Slot,
    validar: bool = False,
    ctx: ContextoRestricoes | None = None,
) -> Horario:
    """Move uma aula para um novo slot.

    Retorna um novo Horario. Não altera nada se o slot de origem ou destino
    for imutável, ou se a aula não existir no horário.

    Se `validar=True` e `ctx` for fornecido, verifica restrições duras após
    o movimento e devolve o horário inalterado se houver violações.
    """

    if _slot_e_imutavel(horario, aula.slot) or _slot_e_imutavel(horario, novo_slot):
        return horario.clone()

    # Verifica se a aula existe no horário
    existe = any(
        a.turma == aula.turma
        and a.disciplina == aula.disciplina
        and a.professor == aula.professor
        and a.sala == aula.sala
        and a.slot == aula.slot
        for a in horario.aulas
    )
    if not existe:
        return horario.clone()

    vizinho = horario.clone()
    vizinho.remover(aula)
    nova_aula = Aula(
        turma=aula.turma,
        disciplina=aula.disciplina,
        professor=aula.professor,
        sala=aula.sala,
        slot=novo_slot,
    )
    vizinho.adicionar(nova_aula)

    if validar and ctx is not None:
        violacoes = verificar_hard(vizinho, ctx)
        if violacoes:
            return horario.clone()

    return vizinho


def trocar_aulas(
    horario: Horario,
    aula1: Aula,
    aula2: Aula,
    validar: bool = False,
    ctx: ContextoRestricoes | None = None,
) -> Horario:
    """Troca os slots de duas aulas.

    Retorna um novo Horario. Não altera nada se qualquer um dos slots for
    imutável, ou se alguma das aulas não existir no horário.

    Se `validar=True` e `ctx` for fornecido, verifica restrições duras após
    o movimento e devolve o horário inalterado se houver violações.
    """

    if _slot_e_imutavel(horario, aula1.slot) or _slot_e_imutavel(horario, aula2.slot):
        return horario.clone()

    vizinho = horario.clone()
    vizinho.remover(aula1)
    vizinho.remover(aula2)

    nova_a1 = Aula(
        turma=aula1.turma,
        disciplina=aula1.disciplina,
        professor=aula1.professor,
        sala=aula1.sala,
        slot=aula2.slot,
    )
    nova_a2 = Aula(
        turma=aula2.turma,
        disciplina=aula2.disciplina,
        professor=aula2.professor,
        sala=aula2.sala,
        slot=aula1.slot,
    )
    vizinho.adicionar(nova_a1)
    vizinho.adicionar(nova_a2)

    if validar and ctx is not None:
        violacoes = verificar_hard(vizinho, ctx)
        if violacoes:
            return horario.clone()

    return vizinho


def remover_aula(horario: Horario, aula: Aula) -> Horario:
    """Remove uma aula do horário.

    Retorna um novo Horario. Não remove se o slot for imutável ou se a aula
    não existir.
    """

    if _slot_e_imutavel(horario, aula.slot):
        return horario.clone()

    existe = any(
        a.turma == aula.turma
        and a.disciplina == aula.disciplina
        and a.professor == aula.professor
        and a.sala == aula.sala
        and a.slot == aula.slot
        for a in horario.aulas
    )
    if not existe:
        return horario.clone()

    vizinho = horario.clone()
    vizinho.remover(aula)
    return vizinho


def validar_apos_movimento(horario: Horario, ctx: ContextoRestricoes) -> list[str]:
    """Executa a verificação de restrições duras após um movimento manual.

    Retorna a lista de violações (vazia = todas as restrições duras respeitadas).
    """

    return verificar_hard(horario, ctx)


def listar_aulas_mutaveis(horario: Horario) -> list[Aula]:
    """Retorna as aulas cujos slots são mutáveis (não são do seed)."""

    return [a for a in horario.aulas if not _slot_e_imutavel(horario, a.slot)]


def listar_aulas_imutaveis(horario: Horario) -> list[Aula]:
    """Retorna as aulas cujos slots são imutáveis (do seed)."""

    return [a for a in horario.aulas if _slot_e_imutavel(horario, a.slot)]
