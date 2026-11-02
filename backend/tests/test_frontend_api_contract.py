"""Garante que os endpoints chamados pelo frontend existem no backend.

Sem este teste, um rename de rota no backend passa despercebido e só se
descobre em runtime com um 404 na UI (foi o caso de /schedule vs /scheduler).
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import FastAPI

from app.api.routers import (
    auth,
    classes,
    courses,
    disputes,
    rooms,
    schedules,
    subjects,
    unavailability,
    users,
)

# Em container, o web source está em /app/web (copiado pelo Dockerfile)
# No host, está em REPO_ROOT/web
REPO_ROOT = Path(__file__).resolve().parents[2]
API_TS = REPO_ROOT / "web" / "src" / "services" / "api.ts"
# Fallback para execução dentro do container
if not API_TS.exists():
    for candidate in (
        Path("/app/web/src/services/api.ts"),
        Path("/github/workspace/web/src/services/api.ts"),
        Path("/workspace/web/src/services/api.ts"),
    ):
        if candidate.exists():
            API_TS = candidate
            break

ROUTERS = (
    auth,
    users,
    rooms,
    subjects,
    classes,
    courses,
    schedules,
    disputes,
    unavailability,
)

_CALL_RE = re.compile(
    r"""api\.(get|post|put|patch|delete)\(\s*[`"']([^`"']+)""",
)
_PARAM_RE = re.compile(r"\$\{[^}]+\}|\{[^}]+\}")


def _normalize(path: str) -> str:
    # Remove trailing slash (FastAPI canonical paths have it)
    path = path.rstrip("/") or "/"
    return _PARAM_RE.sub("{param}", path)


def _backend_openapi() -> dict[str, set[str]]:
    app = FastAPI()
    for module in ROUTERS:
        app.include_router(module.router)
    return {
        _normalize(path): set(methods)
        for path, methods in app.openapi()["paths"].items()
    }


def _frontend_calls() -> set[tuple[str, str]]:
    source = API_TS.read_text(encoding="utf-8")
    return {
        (method.lower(), _normalize(path))
        for method, path in _CALL_RE.findall(source)
    }


def test_frontend_api_calls_exist_in_backend() -> None:
    backend = _backend_openapi()
    missing = sorted(
        f"{method.upper()} {path}"
        for method, path in _frontend_calls()
        if path not in backend or method not in backend[path]
    )
    assert not missing, f"Frontend chama endpoints inexistentes: {missing}"
