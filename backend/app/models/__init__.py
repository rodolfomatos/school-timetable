"""Inicialização dos modelos — exporta todas as classes para facilitar importações."""

from app.models.schedule import (
    Dispute,
    ScheduleAssignment,
    ScheduleVersion,
    Unavailability,
)
from app.models.school import (
    Class,
    Course,
    Room,
    Subject,
    Teacher,
)
from app.models.user import Role, User

__all__ = [
    "User",
    "Role",
    "Course",
    "Room",
    "Subject",
    "Class",
    "Teacher",
    "ScheduleVersion",
    "ScheduleAssignment",
    "Unavailability",
    "Dispute",
]
