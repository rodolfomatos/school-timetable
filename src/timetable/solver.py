"""Interface abstrata para solvers de horário escolar.

Implementações concretas:
- CP-SAT (linha de base exata, OR-Tools) — ver `cp_sat_baseline.py`
- Tabu Search / Simulated Annealing — ver `local_search.py`
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .constraints import ContextoRestricoes
from .models import Horario


class SolverBase(ABC):
    """Contrato de solver."""

    @abstractmethod
    def resolver(
        self,
        horario_inicial: Horario,
        ctx: ContextoRestricoes,
        tempo_limite_segundos: float = 60.0,
    ) -> Horario:
        """Retorna um horário otimizado (ou aproximado) dentro do tempo limite."""

        raise NotImplementedError
