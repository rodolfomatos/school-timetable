"""Modelo de domínio do problema de horário escolar.

Entidades: Slot, Sala, Professor, Turma, Disciplina, Aula, Horario,
RelacaoCasamento, RelacaoFilho.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Slot:
    """Unidade de tempo: (dia_semana, hora)."""

    dia: str  # ex. "segunda", "terca", ...
    hora: int  # ex. 1, 2, 3 ...

    def __hash__(self) -> int:
        return hash((self.dia, self.hora))

    def __str__(self) -> str:
        return f"{self.dia} {self.hora}h"


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

    def esta_disponivel(self, slot: Slot) -> bool:
        if not self.disponibilidade:
            return True
        return slot in self.disponibilidade


@dataclass(frozen=True)
class Turma:
    identificador: str
    ano: int
    numero_alunos: int


@dataclass(frozen=True)
class Disciplina:
    identificador: str
    nome: str
    carga_semanal: int
    tipo_sala_requerida: str = "normal"


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
    """Uma atribuição única: turma, disciplina, professor, sala, slot."""

    turma: str
    disciplina: str
    professor: str
    sala: str
    slot: Slot


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

    def turma_ocupada_em(self, turma: str, slot: Slot) -> bool:
        return any(a.turma == turma and a.slot == slot for a in self.aulas)

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
