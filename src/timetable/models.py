"""Modelo de domínio do problema de horário escolar.

Entidades: Slot, Sala, Professor, Turma, Disciplina, Aula, Horario,
RelacaoCasamento, RelacaoFilho.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Slot:
    """Unidade de tempo com hora de início e fim para cálculo real de períodos."""

    dia: str  # ex. "segunda", "terca", ...
    hora: int  # ex. 1, 2, 3 ...
    hora_inicio: int | None = None  # hora de início real (ex: 8 para 8h)
    hora_fim: int | None = None  # hora de fim real (ex: 9 para 9h)

    def __hash__(self) -> int:
        return hash((self.dia, self.hora))

    def __str__(self) -> str:
        return f"{self.dia} {self.hora}h"

    def eh_manha(self, limite_manha_tarde: int = 12) -> bool:
        """Retorna True se o slot é considerado manhã com base na hora de início."""
        if self.hora_inicio is not None:
            return self.hora_inicio < limite_manha_tarde
        return self.hora < limite_manha_tarde


@dataclass(frozen=True)
class Sala:
    identificador: str
    capacidade: int
    tipo: str = "normal"  # "normal" | "laboratorio"
    dias_disponiveis: frozenset[str] = field(default_factory=frozenset)

    def disponivel_no_dia(self, dia: str) -> bool:
        if not self.dias_disponiveis:
            return True
        return dia in self.dias_disponiveis


@dataclass(frozen=True)
class Professor:
    identificador: str
    nome: str
    disponibilidade: frozenset[Slot] = field(default_factory=frozenset)
    dia_folga_preferido: Optional[str] = None
    prefere_manha: bool = True
    carga_maxima_semanal: int = 30
    carga_minima_semanal: int = 10
    # Disciplinas que o professor está qualificado para lecionar
    qualificacoes: frozenset[str] = field(default_factory=frozenset)
    # Distingue "qualificações não especificadas" (legacy) de "nenhuma
    # qualificação atribuída" (explicitamente vazio).
    qualificacoes_definidas: bool = False

    def esta_disponivel(self, slot: Slot) -> bool:
        if not self.disponibilidade:
            return True
        return slot in self.disponibilidade

    def pode_lecionar(self, disciplina_id: str) -> bool:
        """Retorna True se o professor está qualificado para lecionar a disciplina."""
        if not self.qualificacoes_definidas and not self.qualificacoes:
            # Compatibilidade com versões anteriores: ausência de dados não é
            # tratada como "qualificado para nada".
            return True
        return disciplina_id in self.qualificacoes


@dataclass(frozen=True)
class Turma:
    identificador: str
    ano: int
    numero_alunos: int


@dataclass(frozen=True)
class Subgrupo:
    """Subdivisão de uma turma para disciplinas em regime articulado.

    Exemplo: turma 10º Ano A dividida em "Grupo A" e "Grupo B" para Música,
    onde cada grupo tem aula em horários diferentes.
    """

    identificador: str
    turma_pai: str  # identificador da turma a que pertence
    nome: str  # ex: "Grupo A", "Grupo B", "Subgrupo 1"
    numero_alunos: int


@dataclass(frozen=True)
class Disciplina:
    identificador: str
    nome: str
    carga_semanal: int
    tipo_sala_requerida: str = "normal"


@dataclass(frozen=True)
class SessaoRequerida:
    """Uma sessão lectiva obrigatória, com identidade estável.

    ``professores_elegiveis`` vazio significa que nenhum docente qualificado
    foi encontrado; o construtor de domínio trata isso como erro explícito.
    """

    lesson_id: str
    turma: str
    disciplina: str
    professores_elegiveis: tuple[str, ...] = ()
    subgrupo_id: Optional[str] = None
    duracao_slots: int = 1


@dataclass(frozen=True)
class Diagnostico:
    """Problema detectado ao traduzir dados institucionais para o domínio."""

    codigo: str
    severidade: str  # "ERROR" | "WARNING"
    mensagem: str
    entidades: tuple[str, ...] = ()



@dataclass
class RelacaoCasamento:
    """Dois professores casados não devem dar aula na mesma turma."""

    professor_a: str
    professor_b: str


@dataclass
class RelacaoFilho:
    """Filho de professores casados não deve estar na turma dos pais."""

    professor_pai: str
    professor_mae: str
    identificador_turma_filho: str


@dataclass
class Aula:
    """Uma atribuição única: turma, disciplina, professor, sala, slot.

    Opcionalmente associada a um subgrupo da turma (para disciplinas
    em regime articulado, onde apenas parte dos alunos tem aula).
    """

    turma: str
    disciplina: str
    professor: str
    sala: str
    slot: Slot
    subgrupo_id: Optional[str] = None  # None = toda a turma


@dataclass
class Horario:
    """Coleção de aulas. Oferece consultas de ocupação por entidade."""

    aulas: list[Aula] = field(default_factory=list)
    slots_imutaveis: frozenset[Slot] = field(default_factory=frozenset)

    def adicionar(self, aula: Aula) -> None:
        self.aulas.append(aula)

    def remover(self, aula: Aula) -> None:
        self.aulas.remove(aula)

    def professor_ocupado_em(self, professor: str, slot: Slot) -> bool:
        return any(a.professor == professor and a.slot == slot for a in self.aulas)

    def sala_ocupada_em(self, sala: str, slot: Slot) -> bool:
        return any(a.sala == sala and a.slot == slot for a in self.aulas)

    def turma_ocupada_em(self, turma: str, slot: Slot, subgrupo_id: Optional[str] = None) -> bool:
        """Verifica se uma turma (ou subgrupo específico) está ocupada em um slot.

        Se subgrupo_id for fornecido, verifica esse subgrupo E a turma inteira
        (subgrupo_id=None), pois a turma inteira não pode sobrepor-se a subgrupos.
        Se subgrupo_id=None (turma inteira), verifica todos os subgrupos dessa turma.
        """
        if subgrupo_id is not None:
            # Verifica o subgrupo específico E a turma inteira
            return any(
                a.turma == turma and (a.subgrupo_id == subgrupo_id or a.subgrupo_id is None) and a.slot == slot
                for a in self.aulas
            )
        else:
            # Turma inteira: verifica todos os subgrupos dessa turma
            return any(
                a.turma == turma and a.slot == slot
                for a in self.aulas
            )

    def aulas_do_professor(self, professor: str) -> list[Aula]:
        return [a for a in self.aulas if a.professor == professor]

    def aulas_da_turma(self, turma: str) -> list[Aula]:
        return [a for a in self.aulas if a.turma == turma]

    def aulas_da_disciplina(self, disciplina: str) -> list[Aula]:
        return [a for a in self.aulas if a.disciplina == disciplina]

    def slot_e_imutavel(self, slot: Slot) -> bool:
        return slot in self.slots_imutaveis

    def clone(self) -> "Horario":
        novo = Horario(
            aulas=list(self.aulas),
            slots_imutaveis=self.slots_imutaveis,
        )
        return novo
