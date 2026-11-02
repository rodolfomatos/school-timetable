"""Cria contas de demonstração usadas pelos testes E2E.

Idempotente: contas existentes são ignoradas.
"""

from __future__ import annotations

import asyncio

from app.db.session import engine
from app.models.user import Role

from scripts.create_user import create_user

DEMO_PASSWORD = "senha123"

DEMO_USERS = (
    ("admin@escola.pt", Role.ADMIN, "Administrador Demo"),
    ("professor@escola.pt", Role.TEACHER, "Professor Demo"),
    ("aluno@escola.pt", Role.STUDENT, "Aluno Demo"),
)


async def main() -> None:
    try:
        for email, role, name in DEMO_USERS:
            await create_user(
                email=email,
                password=DEMO_PASSWORD,
                role=role,
                full_name=name,
                institution_id=None,
                skip_existing=True,
            )
    finally:
        await engine.dispose()
    print(f"Contas demo prontas (palavra-passe: {DEMO_PASSWORD})")


if __name__ == "__main__":
    asyncio.run(main())
