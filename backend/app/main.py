"""Aplicação FastAPI principal."""

from __future__ import annotations

import os
import subprocess
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
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


def run_migrations():
    """Executa migrações Alembic na inicialização."""
    try:
        # Run alembic upgrade head
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"Alembic migration failed: {result.stderr}", file=sys.stderr)
            raise RuntimeError(f"Database migration failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Database migration timed out")
    except Exception as e:
        raise RuntimeError(f"Failed to run database migrations: {e}")


def validate_production_config():
    """Valida configuração de produção - falha se secrets de desenvolvimento forem usados."""
    if settings.ENVIRONMENT == "production":
        # Verificar SECRET_KEY não é a padrão
        if settings.SECRET_KEY == "dev-secret-key-change-in-production":
            raise RuntimeError(
                "SECURITY ERROR: SECRET_KEY is set to development default. "
                "Set a strong SECRET_KEY in production environment."
            )
        # Verificar DATABASE_URL não contém credenciais padrão
        if "school:school@localhost" in settings.DATABASE_URL:
            raise RuntimeError(
                "SECURITY ERROR: DATABASE_URL uses development credentials. "
                "Set proper DATABASE_URL in production environment."
            )
        # Verificar se não está em modo debug
        if settings.ENVIRONMENT == "production" and os.getenv("DEBUG") == "1":
            raise RuntimeError(
                "SECURITY ERROR: DEBUG mode enabled in production."
            )


app = FastAPI(
    title="School Timetable API",
    description="Gerador de horários escolares com IA e gestão de contestações",
    version="0.2.0",
)

# Validar configuração de produção ANTES de configurar a app
validate_production_config()

# Executar migrações na inicialização
run_migrations()

# Estado do limiter anexado à app
# (limiter é importado de app.core.limiter)


# Estado do limiter anexado à app
app.state.limiter = limiter

# Handler para exceder o rate limit
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir routers

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(subjects.router)
app.include_router(classes.router)
app.include_router(courses.router)
app.include_router(schedules.router)
app.include_router(disputes.router)


@app.get("/health")
async def health():
    """Endpoint de saúde para Docker."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Endpoint raiz."""
    return {
        "message": "School Timetable API",
        "version": "0.2.0",
        "docs": "/docs",
    }