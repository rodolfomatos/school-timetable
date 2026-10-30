"""Verificação de restrições duras e moles.

Toda restrição dura deve ser satisfeita para a solução ser viável.
Restrições moles geram penalidades aditivas na função objetivo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models import (
    Aula,
    Disciplina,
    Horario,
    Professor,
    RelacaoCasamento,
    RelacaoFilho,
    Sala,
    Slot,
    Turma,
)


@dataclass
class ContextoRestricoes:
    """Conjunto de dados auxiliares para verificação de restrições."""

    professores: dict[str, Professor]
    salas: dict[str, Sala]
    turmas: dict[str, Turma]
    disciplinas: dict[str, Disciplina]
    casamentos: list[RelacaoCasamento]
    relacoes_filho: list[RelacaoFilho]

    def professor_por_id(self, identificador: str) -> Optional[Professor]:
        return self.professores.get(identificador)

    def sala_por_id(self, identificador: str) -> Optional[Sala]:
        return self.salas.get(identificador)

    def disciplina_por_id(self, identificador: str) -> Optional[Disciplina]:
        return self.disciplinas.get(identificador)


@dataclass
class PenalidadeMole:
    id_restricao: str
    descricao: str
    valor: int


def verificar_hard(horario: Horario, ctx: ContextoRestricoes) -> list[str]:
    """Retorna lista de violações de restrições duras (vazia = viável)."""

    violacoes: list[str] = []

    # H01: professor não dá duas aulas no mesmo slot
    professor_slot: dict[tuple[str, Slot], int] = {}
    for aula in horario.aulas:
        chave = (aula.professor, aula.slot)
        professor_slot[chave] = professor_slot.get(chave, 0) + 1
    for (prof, slot), count in professor_slot.items():
        if count > 1:
            violacoes.append(f"H01: professor {prof} em {slot} em {count} aulas")

    # H02: sala não alberga duas aulas no mesmo slot
    sala_slot: dict[tuple[str, Slot], int] = {}
    for aula in horario.aulas:
        chave = (aula.sala, aula.slot)
        sala_slot[chave] = sala_slot.get(chave, 0) + 1
    for (sala, slot), count in sala_slot.items():
        if count > 1:
            violacoes.append(f"H02: sala {sala} em {slot} com {count} aulas")

    # H03: turma não tem duas aulas no mesmo slot
    turma_slot: dict[tuple[str, Slot], int] = {}
    for aula in horario.aulas:
        chave = (aula.turma, aula.slot)
        turma_slot[chave] = turma_slot.get(chave, 0) + 1
    for (turm, slot), count in turma_slot.items():
        if count > 1:
            violacoes.append(f"H03: turma {turm} em {slot} com {count} aulas")

    # H04: sala compatível com a disciplina
    for aula in horario.aulas:
        sala = ctx.sala_por_id(aula.sala)
        disc = ctx.disciplina_por_id(aula.disciplina)
        if sala and disc and sala.tipo != disc.tipo_sala_requerida:
            violacoes.append(
                f"H04: sala {aula.sala} ({sala.tipo}) não serve "
                f"{aula.disciplina} ({disc.tipo_sala_requerida})"
            )

    # H05: professor disponível nesse slot
    for aula in horario.aulas:
        prof = ctx.professor_por_id(aula.professor)
        if prof and not prof.esta_disponivel(aula.slot):
            violacoes.append(f"H05: professor {aula.professor} não disponível em {aula.slot}")

    # H07: professores casados não na mesma turma
    casados = {(c.professor_a, c.professor_b) for c in ctx.casamentos} | {
        (c.professor_b, c.professor_a) for c in ctx.casamentos
    }
    turma_professores: dict[tuple[str, Slot], list[str]] = {}
    for aula in horario.aulas:
        chave = (aula.turma, aula.slot)
        turma_professores.setdefault(chave, []).append(aula.professor)
    for (turm, slot), profs in turma_professores.items():
        for i, pa in enumerate(profs):
            for pb in profs[i + 1 :]:
                if (pa, pb) in casados:
                    violacoes.append(
                        f"H07: professores casados {pa} e {pb} na turma {turm} em {slot}"
                    )

    # H08: filho não na turma dos pais casados
    for rel in ctx.relacoes_filho:
        for aula in horario.aulas:
            if aula.turma == rel.identificador_turma_filho:
                if aula.professor in (rel.professor_pai, rel.professor_mae):
                    violacoes.append(
                        f"H08: {aula.professor} (pai/me) leciona na turma "
                        f"do filho {rel.identificador_turma_filho}"
                    )

    return violacoes


def calcular_penalidades_moles(horario: Horario, ctx: ContextoRestricoes) -> list[PenalidadeMole]:
    """Calcula penalidades das restrições moles (adiitivas)."""

    penalidades: list[PenalidadeMole] = []

    # S01: dia de folga preferido do professor
    for aula in horario.aulas:
        prof = ctx.professor_por_id(aula.professor)
        if prof and prof.dia_folga_preferido and aula.slot.dia == prof.dia_folga_preferido:
            penalidades.append(
                PenalidadeMole(
                    id_restricao="S01",
                    descricao=(
                        f"Professor {aula.professor} aula no dia de folga "
                        f"preferido {prof.dia_folga_preferido}"
                    ),
                    valor=10,
                )
            )

    # S02: preferência manhã/tarde
    for aula in horario.aulas:
        prof = ctx.professor_por_id(aula.professor)
        if prof and prof.prefere_manha and aula.slot.hora >= 13:
            penalidades.append(
                PenalidadeMole(
                    id_restricao="S02",
                    descricao=(f"Professor {aula.professor} aula à tarde (prefere manhã)"),
                    valor=8,
                )
            )

    # S03: duas horas consecutivas da mesma disciplina para a mesma turma
    aulas_por_turma_disc: dict[tuple[str, str], list[Aula]] = {}
    for aula in horario.aulas:
        chave = (aula.turma, aula.disciplina)
        aulas_por_turma_disc.setdefault(chave, []).append(aula)
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
            penalidades.append(
                PenalidadeMole(
                    id_restricao="S03",
                    descricao=(f"Turma {turm} / {disc} sem duas horas consecutivas"),
                    valor=6,
                )
            )

    # S08: professor a trabalhar muitos dias seguidos sem pausa
    aulas_por_prof: dict[str, list[Aula]] = {}
    for aula in horario.aulas:
        aulas_por_prof.setdefault(aula.professor, []).append(aula)
    for prof_id, aulas in aulas_por_prof.items():
        dias_com_aula = sorted({a.slot.dia for a in aulas})
        if len(dias_com_aula) >= 5:
            penalidades.append(
                PenalidadeMole(
                    id_restricao="S08",
                    descricao=(
                        f"Professor {prof_id} leciona em {len(dias_com_aula)} "
                        f"dias diferentes (risco de falta de pausa)"
                    ),
                    valor=12,
                )
            )

    # S09: distribuição desigual entre professores da mesma disciplina
    aulas_por_disc_prof: dict[tuple[str, str], int] = {}
    for aula in horario.aulas:
        chave = (aula.disciplina, aula.professor)
        aulas_por_disc_prof[chave] = aulas_por_disc_prof.get(chave, 0) + 1
    disciplinas_professores: dict[str, list[int]] = {}
    for (disc, prof_id), count in aulas_por_disc_prof.items():
        disciplinas_professores.setdefault(disc, []).append(count)
    for disc, contagens in disciplinas_professores.items():
        if len(contagens) > 1:
            diferenca = max(contagens) - min(contagens)
            if diferenca > 2:
                penalidades.append(
                    PenalidadeMole(
                        id_restricao="S09",
                        descricao=(
                            f"Disciplina {disc} com distribuição desigual "
                            f"entre professores (diferença de {diferenca} aulas)"
                        ),
                        valor=11,
                    )
                )

    # S10: carga concentrada em poucos dias para o mesmo professor
    for prof_id, aulas in aulas_por_prof.items():
        dias_com_aula = {a.slot.dia for a in aulas}
        if len(dias_com_aula) <= 2 and len(aulas) >= 5:
            penalidades.append(
                PenalidadeMole(
                    id_restricao="S10",
                    descricao=(
                        f"Professor {prof_id} com {len(aulas)} aulas concentradas "
                        f"em {len(dias_com_aula)} dias"
                    ),
                    valor=10,
                )
            )

    # S04: disciplinas não espalhadas pela semana (todas as aulas de uma
    # disciplina para uma turma num único dia)
    aulas_por_turma_disc_dia: dict[tuple[str, str, str], list[Aula]] = {}
    for aula in horario.aulas:
        chave = (aula.turma, aula.disciplina, aula.slot.dia)
        aulas_por_turma_disc_dia.setdefault(chave, []).append(aula)
    disciplinas_por_turma_dia: dict[tuple[str, str], set[str]] = {}
    for (turm, disc, dia), aulas in aulas_por_turma_disc_dia.items():
        disciplinas_por_turma_dia.setdefault((turm, disc), set()).add(dia)
    for (turm, disc), dias in disciplinas_por_turma_dia.items():
        if (
            len(dias) == 1
            and sum(len(aulas_por_turma_disc_dia.get((turm, disc, d), [])) for d in dias) >= 2
        ):
            penalidades.append(
                PenalidadeMole(
                    id_restricao="S04",
                    descricao=(
                        f"Turma {turm} / {disc} com todas as aulas "
                        f"concentradas num único dia ({next(iter(dias))})"
                    ),
                    valor=5,
                )
            )

    # S05: padrão A-B-C-A (mesma disciplina interrompida por outra no mesmo dia)
    aulas_por_turma_dia: dict[tuple[str, str], list[tuple[int, str]]] = {}
    for aula in horario.aulas:
        chave = (aula.turma, aula.slot.dia)
        aulas_por_turma_dia.setdefault(chave, []).append((aula.slot.hora, aula.disciplina))
    for (turm, dia), aulas_hora_disc in aulas_por_turma_dia.items():
        aulas_hora_disc.sort()
        disciplinas_ordenadas = [disc for _, disc in aulas_hora_disc]
        for i in range(len(disciplinas_ordenadas) - 2):
            if (
                disciplinas_ordenadas[i] == disciplinas_ordenadas[i + 2]
                and disciplinas_ordenadas[i] != disciplinas_ordenadas[i + 1]
            ):
                penalidades.append(
                    PenalidadeMole(
                        id_restricao="S05",
                        descricao=(
                            f"Turma {turm} em {dia}: padrão A-B-C-A "
                            f"({disciplinas_ordenadas[i]}-{disciplinas_ordenadas[i + 1]}-"
                            f"{disciplinas_ordenadas[i + 2]})"
                        ),
                        valor=7,
                    )
                )
                break  # uma penalidade por turma/dia

    # S06: falta de duas horas consecutivas para avaliação (professores com
    # carga >= 4 devem ter pelo menos um bloco de 2h consecutivas)
    aulas_por_prof_dia: dict[tuple[str, str], list[int]] = {}
    for aula in horario.aulas:
        prof = ctx.professor_por_id(aula.professor)
        if prof and prof.carga_maxima_semanal >= 4:
            chave = (aula.professor, aula.slot.dia)
            aulas_por_prof_dia.setdefault(chave, []).append(aula.slot.hora)
    for (prof_id, dia), horas in aulas_por_prof_dia.items():
        horas.sort()
        tem_bloco_consecutivo = any(horas[i] + 1 == horas[i + 1] for i in range(len(horas) - 1))
        if not tem_bloco_consecutivo and len(horas) >= 2:
            penalidades.append(
                PenalidadeMole(
                    id_restricao="S06",
                    descricao=(
                        f"Professor {prof_id} sem bloco de 2h consecutivas em {dia} para avaliação"
                    ),
                    valor=9,
                )
            )

    # S07: carga horária do professor fora dos limites
    for prof_id, aulas in aulas_por_prof.items():
        prof = ctx.professor_por_id(prof_id)
        if prof:
            total_aulas = len(aulas)
            if total_aulas < prof.carga_minima_semanal or total_aulas > prof.carga_maxima_semanal:
                penalidades.append(
                    PenalidadeMole(
                        id_restricao="S07",
                        descricao=(
                            f"Professor {prof_id} com {total_aulas} aulas/semana "
                            f"(fora dos limites [{prof.carga_minima_semanal}, "
                            f"{prof.carga_maxima_semanal}])"
                        ),
                        valor=8,
                    )
                )

    return penalidades
