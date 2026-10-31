"""Dependências de base de dados para testes."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Fornece uma sessão de base de dados para testes."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
