"""Camada de domínio canónica, independente do ORM.

Traduz dados institucionais (turmas, disciplinas, docentes, salas, currículo e
indisponibilidades) num ``ProblemInstance`` explícito. Nenhum objecto SQLAlchemy
entra aqui: o backend adapta o ORM para estes DTOs.

Regras centrais:
- só existem sessões para relações curriculares explícitas;
- docentes sem qualificação para a disciplina não são elegíveis;
- indisponibilidades persistidas e adicionais são aplicadas;
- capacidade e tipo de sala são validados antes de criar sessões;
- dados incompletos produzem ``Diagnostico`` com severidade explícita.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, replace
from typing import Iterable, Mapping, Optional

from .constraints import ContextoRestricoes
from .models import (
    Diagnostico,
    Disciplina,
    Professor,
    RelacaoCasamento,
    RelacaoFilho,
    Sala,
    SessaoRequerida,
    Slot,
    Subgrupo,
    Turma,
)

DIAS_PADRAO = ("segunda", "terca", "quarta", "quinta", "sexta")


@dataclass(frozen=True)
class EntradaCurricular:
    """Relação curricular válida: turma + disciplina (+ docentes elegíveis)."""

    turma_id: str
    disciplina_id: str
    professores_elegiveis: tuple[str, ...] = ()
    subgrupo_id: Optional[str] = None


@dataclass
class ProblemInstance:
    """Problema de timetabling completo e consistente, pronto para o solver."""

    professores: dict[str, Professor]
    salas: dict[str, Sala]
    turmas: dict[str, Turma]
    disciplinas: dict[str, Disciplina]
    sessoes: list[SessaoRequerida] = field(default_factory=list)
    casamentos: list[RelacaoCasamento] = field(default_factory=list)
    relacoes_filho: list[RelacaoFilho] = field(default_factory=list)
    subgrupos: dict[str, Subgrupo] = field(default_factory=dict)
    diagnosticos: list[Diagnostico] = field(default_factory=list)

    @property
    def tem_erros(self) -> bool:
        """True se algum diagnóstico impede a construção de um horário válido."""

        return any(d.severidade == "ERROR" for d in self.diagnosticos)

    def diagnosticos_dict(self) -> list[dict]:
        """Representação serializável para a API."""

        return [
            {
                "codigo": d.codigo,
                "severidade": d.severidade,
                "mensagem": d.mensagem,
                "entidades": list(d.entidades),
            }
            for d in self.diagnosticos
        ]

    def para_contexto(self) -> ContextoRestricoes:
        """Converte o problema para o contexto usado pelo solver e validador."""

        return ContextoRestricoes(
            professores=dict(self.professores),
            salas=dict(self.salas),
            turmas=dict(self.turmas),
            disciplinas=dict(self.disciplinas),
            casamentos=list(self.casamentos),
            relacoes_filho=list(self.relacoes_filho),
            subgrupos=dict(self.subgrupos),
            sessoes_requeridas=list(self.sessoes),
        )


def _slots_padrao() -> list[Slot]:
    return [Slot(dia=dia, hora=hora) for dia in DIAS_PADRAO for hora in range(8, 18)]


def _normalizar_indisponibilidades(
    indisponibilidades: Mapping[str, Iterable[Slot]] | None,
    adicionais: Mapping[str, Iterable[Slot]] | None,
) -> dict[str, set[Slot]]:
    resultado: dict[str, set[Slot]] = defaultdict(set)
    for origem in (indisponibilidades or {}, adicionais or {}):
        for professor_id, slots in origem.items():
            resultado[professor_id].update(slots)
    return resultado


def construir_problema(
    *,
    professores: Mapping[str, Professor],
    salas: Mapping[str, Sala],
    turmas: Mapping[str, Turma],
    disciplinas: Mapping[str, Disciplina],
    curriculo: Iterable[EntradaCurricular],
    indisponibilidades: Mapping[str, Iterable[Slot]] | None = None,
    indisponibilidades_adicionais: Mapping[str, Iterable[Slot]] | None = None,
    subgrupos: Mapping[str, Subgrupo] | None = None,
    casamentos: Iterable[RelacaoCasamento] = (),
    relacoes_filho: Iterable[RelacaoFilho] = (),
    slots_possiveis: Iterable[Slot] | None = None,
) -> ProblemInstance:
    """Constrói um ``ProblemInstance`` validado a partir de dados institucionais."""

    diagnosticos: list[Diagnostico] = []
    subgrupos = dict(subgrupos or {})
    entradas = list(curriculo)

    # Universo de slots: explícito, ou união das disponibilidades, ou padrão.
    slots = list(slots_possiveis) if slots_possiveis is not None else []
    if not slots:
        for prof in professores.values():
            slots.extend(prof.disponibilidade)
    if not slots:
        slots = _slots_padrao()
    universo_slots = frozenset(slots)

    indisponivel = _normalizar_indisponibilidades(
        indisponibilidades, indisponibilidades_adicionais
    )

    professores_normalizados: dict[str, Professor] = {}
    for prof_id, prof in professores.items():
        bloqueados = indisponivel.get(prof_id, set())
        if prof.disponibilidade:
            disponiveis = frozenset(prof.disponibilidade) - bloqueados
        else:
            diagnosticos.append(
                Diagnostico(
                    codigo="DISPONIBILIDADE_NAO_ESPECIFICADA",
                    severidade="WARNING",
                    mensagem=(
                        f"Docente {prof_id} sem disponibilidade explícita; "
                        "assume-se disponível em todos os slots excepto "
                        "indisponibilidades declaradas."
                    ),
                    entidades=(prof_id,),
                )
            )
            disponiveis = universo_slots - bloqueados

        if not disponiveis:
            diagnosticos.append(
                Diagnostico(
                    codigo="SEM_DISPONIBILIDADE",
                    severidade="ERROR",
                    mensagem=f"Docente {prof_id} não tem qualquer slot disponível.",
                    entidades=(prof_id,),
                )
            )
        professores_normalizados[prof_id] = replace(
            prof, disponibilidade=frozenset(disponiveis)
        )

    if not entradas:
        diagnosticos.append(
            Diagnostico(
                codigo="CURRICULO_VAZIO",
                severidade="ERROR",
                mensagem="Não existe qualquer relação curricular turma-disciplina.",
            )
        )

    sessoes: list[SessaoRequerida] = []
    vistos: set[tuple[str, str, Optional[str]]] = set()

    for entrada in entradas:
        turma = turmas.get(entrada.turma_id)
        disciplina = disciplinas.get(entrada.disciplina_id)
        if turma is None:
            diagnosticos.append(
                Diagnostico(
                    codigo="TURMA_INEXISTENTE",
                    severidade="ERROR",
                    mensagem=f"Turma {entrada.turma_id} referida no currículo não existe.",
                    entidades=(entrada.turma_id,),
                )
            )
            continue
        if disciplina is None:
            diagnosticos.append(
                Diagnostico(
                    codigo="DISCIPLINA_INEXISTENTE",
                    severidade="ERROR",
                    mensagem=(
                        f"Disciplina {entrada.disciplina_id} referida no currículo "
                        f"da turma {entrada.turma_id} não existe."
                    ),
                    entidades=(entrada.turma_id, entrada.disciplina_id),
                )
            )
            continue

        chave = (entrada.turma_id, entrada.disciplina_id, entrada.subgrupo_id)
        if chave in vistos:
            diagnosticos.append(
                Diagnostico(
                    codigo="CURRICULO_DUPLICADO",
                    severidade="ERROR",
                    mensagem=(
                        f"Relação curricular duplicada: turma {entrada.turma_id}, "
                        f"disciplina {entrada.disciplina_id}, "
                        f"subgrupo {entrada.subgrupo_id or 'turma inteira'}."
                    ),
                    entidades=(
                        entrada.turma_id,
                        entrada.disciplina_id,
                        entrada.subgrupo_id or "",
                    ),
                )
            )
            continue
        vistos.add(chave)

        numero_alunos = turma.numero_alunos
        if entrada.subgrupo_id is not None:
            subgrupo = subgrupos.get(entrada.subgrupo_id)
            if subgrupo is None or subgrupo.turma_pai != entrada.turma_id:
                diagnosticos.append(
                    Diagnostico(
                        codigo="SUBGRUPO_INVALIDO",
                        severidade="ERROR",
                        mensagem=(
                            f"Subgrupo {entrada.subgrupo_id} não pertence à turma "
                            f"{entrada.turma_id}."
                        ),
                        entidades=(entrada.turma_id, entrada.subgrupo_id),
                    )
                )
                continue
            numero_alunos = subgrupo.numero_alunos

        # Docentes elegíveis: explícitos na relação curricular ou todos os
        # qualificados para a disciplina. Nunca "todos os docentes".
        candidatos = (
            list(entrada.professores_elegiveis)
            if entrada.professores_elegiveis
            else [p for p in professores_normalizados if professores_normalizados[p].pode_lecionar(entrada.disciplina_id)]
        )
        elegiveis: list[str] = []
        for prof_id in candidatos:
            prof = professores_normalizados.get(prof_id)
            if prof is None:
                diagnosticos.append(
                    Diagnostico(
                        codigo="PROFESSOR_INEXISTENTE",
                        severidade="ERROR",
                        mensagem=f"Docente {prof_id} referido no currículo não existe.",
                        entidades=(entrada.turma_id, entrada.disciplina_id, prof_id),
                    )
                )
                continue
            if not prof.pode_lecionar(entrada.disciplina_id):
                diagnosticos.append(
                    Diagnostico(
                        codigo="PROFESSOR_NAO_QUALIFICADO",
                        severidade="WARNING",
                        mensagem=(
                            f"Docente {prof_id} não está qualificado para "
                            f"{entrada.disciplina_id}; excluído."
                        ),
                        entidades=(prof_id, entrada.disciplina_id),
                    )
                )
                continue
            elegiveis.append(prof_id)

        if not elegiveis:
            diagnosticos.append(
                Diagnostico(
                    codigo="SEM_PROFESSOR_ELEGIVEL",
                    severidade="ERROR",
                    mensagem=(
                        f"Turma {entrada.turma_id}, disciplina "
                        f"{entrada.disciplina_id}: nenhum docente qualificado."
                    ),
                    entidades=(entrada.turma_id, entrada.disciplina_id),
                )
            )
            continue

        salas_compativeis = [
            sala_id
            for sala_id, sala in salas.items()
            if sala.tipo == disciplina.tipo_sala_requerida
            and sala.capacidade >= numero_alunos
        ]
        if not salas_compativeis:
            diagnosticos.append(
                Diagnostico(
                    codigo="SEM_SALA_COMPATIVEL",
                    severidade="ERROR",
                    mensagem=(
                        f"Turma {entrada.turma_id}, disciplina "
                        f"{entrada.disciplina_id}: nenhuma sala do tipo "
                        f"{disciplina.tipo_sala_requerida} com capacidade >= "
                        f"{numero_alunos}."
                    ),
                    entidades=(entrada.turma_id, entrada.disciplina_id),
                )
            )
            continue

        if disciplina.carga_semanal <= 0:
            diagnosticos.append(
                Diagnostico(
                    codigo="CARGA_INVALIDA",
                    severidade="ERROR",
                    mensagem=(
                        f"Disciplina {entrada.disciplina_id} tem carga semanal "
                        f"inválida ({disciplina.carga_semanal})."
                    ),
                    entidades=(entrada.disciplina_id,),
                )
            )
            continue

        for indice in range(disciplina.carga_semanal):
            prefixo = entrada.subgrupo_id or "ALL"
            lesson_id = (
                f"{entrada.turma_id}_{prefixo}_{entrada.disciplina_id}_{indice}"
            )
            sessoes.append(
                SessaoRequerida(
                    lesson_id=lesson_id,
                    turma=entrada.turma_id,
                    disciplina=entrada.disciplina_id,
                    professores_elegiveis=tuple(sorted(elegiveis)),
                    subgrupo_id=entrada.subgrupo_id,
                )
            )

    return ProblemInstance(
        professores=professores_normalizados,
        salas=dict(salas),
        turmas=dict(turmas),
        disciplinas=dict(disciplinas),
        sessoes=sessoes,
        casamentos=list(casamentos),
        relacoes_filho=list(relacoes_filho),
        subgrupos=subgrupos,
        diagnosticos=diagnosticos,
    )
