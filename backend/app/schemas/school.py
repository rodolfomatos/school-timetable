"""Schemas Pydantic para entidades da escola."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any
from pydantic import BaseModel, Field, ConfigDict

IntPK = Annotated[int, Field(gt=0)]


# --- Course ---
class CourseBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: str | None = None


class CourseRead(CourseBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Room ---
class RoomBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0)
    room_type: str = "normal"
    allowed_courses: list[str] | None = None
    reserved_times: list[dict[str, Any]] | None = None
    setup_before: int = Field(default=0, ge=0)
    cleanup_after: int = Field(default=0, ge=0)
    course_id: int | None = None
    is_active: bool = True


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = None
    room_type: str | None = None
    allowed_courses: list[str] | None = None
    reserved_times: list[dict[str, Any]] | None = None
    setup_before: int | None = None
    cleanup_after: int | None = None
    course_id: int | None = None
    is_active: bool | None = None


class RoomRead(RoomBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Subject ---
class SubjectBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    weekly_load: int = Field(gt=0)
    room_type_required: str = "normal"
    periodicity: str = "semanal"
    weeks_active: list[int] | None = None
    course_id: int


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: str | None = None
    weekly_load: int | None = None
    room_type_required: str | None = None
    periodicity: str | None = None
    weeks_active: list[int] | None = None
    course_id: int | None = None
    is_active: bool | None = None


class SubjectRead(SubjectBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Class ---
class ClassBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    course_id: int
    year: int = Field(gt=0)
    student_count: int = Field(gt=0)
    weeks_active: list[int] | None = None
    is_active: bool = True


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    name: str | None = None
    course_id: int | None = None
    year: int | None = None
    student_count: int | None = None
    weeks_active: list[int] | None = None
    is_active: bool | None = None


class ClassRead(ClassBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Teacher ---
class TeacherBase(BaseModel):
    employee_code: str | None = None
    day_off_preferred: str | None = None
    morning_preferred: bool = True
    lunch_sacred: bool = False
    commute_time: int = Field(default=0, ge=0)
    availability: dict | None = None
    is_active: bool = True


class TeacherCreate(TeacherBase):
    user_id: int


class TeacherUpdate(BaseModel):
    employee_code: str | None = None
    day_off_preferred: str | None = None
    morning_preferred: bool | None = None
    lunch_sacred: bool | None = None
    commute_time: int | None = None
    availability: dict | None = None
    is_active: bool | None = None


class TeacherRead(TeacherBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
