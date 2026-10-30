"""Aplicação FastAPI principal."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.db.session import engine, Base
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


async def init_db():
    """Cria todas as tabelas na base de dados."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Limiter de taxa: 5 requisições por minuto por IP para endpoints sensíveis
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="School Timetable API",
    description="Gerador de horários escolares com IA e gestão de contestações",
    version="0.2.0",
)

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


@app.on_event("startup")
async def startup():
    await init_db()


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
