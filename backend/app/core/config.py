"""Configurações da aplicação a partir de variáveis de ambiente."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente ou ficheiro .env."""

    # Base de dados
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://school:school@localhost:5432/school_timetable"
    )

    # Segurança
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Solver
    SOLVER_TIMEOUT_SECONDS: int = Field(default=60)
    SOLVER_MAX_WORKERS: int = Field(default=4)

    # Frontend (para CORS)
    FRONTEND_URL: str = Field(default="http://localhost:3000")

    # Ambiente
    ENVIRONMENT: str = Field(default="development")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
