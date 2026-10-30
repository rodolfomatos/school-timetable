"""Exporta todos os routers para facilitar importações no main.py."""

from app.api.routers import (
    auth,
    users,
    rooms,
    subjects,
    classes,
    courses,
    schedules,
    disputes,
)

__all__ = [
    "auth",
    "users",
    "rooms",
    "subjects",
    "classes",
    "courses",
    "schedules",
    "disputes",
]
