"""Configuração da base de dados assíncrona com SQLAlchemy 2.0."""

from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.base import Base

# Use settings for DATABASE_URL but ensure async driver for SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://school:school@localhost:5432/school_timetable",
)

# Ensure async driver for SQLite
if "sqlite://" in DATABASE_URL and "aiosqlite" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

__all__ = ["engine", "AsyncSessionLocal", "Base"]