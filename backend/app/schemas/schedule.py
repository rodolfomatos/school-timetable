"""Schemas Pydantic para horários, indisponibilidades e contestações."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

IntPK = Annotated[int, Field(gt=0)]

HTML_TAG_RE = re.compile(r"<[^>]*>")


def _no_html(value: str) -> str:
    """Rejeita strings que contenham tags HTML (prevenção XSS)."""
    if HTML_TAG_RE.search(value or ""):
        raise ValueError("Não são permitidas tags HTML neste campo")
    return value


# --- Schedule Version ---
class ScheduleVersionBase(BaseModel):
    institution_id: str | None = None
    status: str = "draft"
    solver_used: str | None = None
    score: int | None = None
    hard_violations: int = 0
    soft_penalties: int = 0


class ScheduleVersionCreate(ScheduleVersionBase):
    pass


class ScheduleVersionRead(ScheduleVersionBase):
    id: int
    created_at: datetime
    published_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# --- Schedule Assignment ---
class Slot(BaseModel):
    dia: str
    hora: int


class ScheduleAssignmentBase(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: int
    room_id: int
    slot: Slot


class ScheduleAssignmentCreate(ScheduleAssignmentBase):
    pass


class ScheduleAssignmentRead(ScheduleAssignmentBase):
    id: int
    version_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Solver Run Request ---
class SolverRunRequest(BaseModel):
    institution_id: str | None = None
    solver: str = "simulated_annealing"  # cp_sat, tabu_search, simulated_annealing
    time_limit_seconds: int = Field(default=60, gt=0, le=3600)
    # Restrições adicionais (indisponibilidades já estão na BD, mas pode-se passar extras)
    additional_unavailabilities: list[dict[str, Any]] | None = None


class SolverRunResponse(BaseModel):
    task_id: str
    status: str
    message: str


class SolverStatusResponse(BaseModel):
    task_id: str
    status: str  # pending, running, completed, failed
    schedule_version_id: int | None = None
    score: int | None = None
    hard_violations: int | None = None
    soft_penalties: int | None = None
    error: str | None = None


# --- Unavailability ---
class Justification(str):
    DESLOCAMENTO = "deslocamento"
    FOLGA = "folga"
    ALMOCO = "almoço"
    COMPROMISSO = "compromisso"
    DOENCA = "doença"
    OUTRO = "outro"


class UnavailabilityBase(BaseModel):
    slot: dict[str, Any]  # {"dia": "segunda", "hora": 1}
    justification: str
    reason: str | None = None

    @field_validator("justification", "reason")
    @classmethod
    def _no_html(cls, v: str | None) -> str | None:
        if v is not None:
            return _no_html(v)
        return v


class UnavailabilityCreate(UnavailabilityBase):
    teacher_id: int


class UnavailabilityRead(UnavailabilityBase):
    id: int
    teacher_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Dispute ---
class DisputeBase(BaseModel):
    assignment_id: int
    reason: str = Field(min_length=1)
    justification: str

    @field_validator("reason", "justification")
    @classmethod
    def _no_html(cls, v: str) -> str:
        return _no_html(v)


class DisputeCreate(DisputeBase):
    teacher_id: int


class DisputeUpdate(BaseModel):
    status: str  # accepted, rejected


class DisputeRead(DisputeBase):
    id: int
    teacher_id: int
    status: str
    created_at: datetime
    resolved_at: datetime | None = None
    resolved_by: int | None = None

    model_config = ConfigDict(from_attributes=True)
