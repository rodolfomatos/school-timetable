---
ticket: T061
title: Fix `make start` — Postgres, backend e healthchecks
sprint: hotfix
priority: high
status: done
created: 2026-11-02
---

# T061 — Fix `make start`

## Context

`make start` falhava em cascata: o Postgres não arrancava, o backend crashava no
import e o healthcheck do backend reportava `unhealthy` mesmo com a app a
responder 200. O objectivo era ter a stack completa (postgres + backend +
frontend) saudável.

## Causas raiz

1. `postgres` usava `POSTGRES_*_FILE: /run/secrets/...`, mas o serviço não
   declarava `secrets:` — os ficheiros nunca eram montados no contentor.
2. `scripts/init-db.sh` definia `shared_preload_libraries = 'pg_stat_statements'`
   em runtime e logo depois `pg_stat_statements.track`; o módulo só carrega
   após restart, pelo que o `ALTER SYSTEM` falhava e, com `set -e`, matava o
   contentor.
3. `backend/requirements.txt` não incluía `email-validator`, necessário para
   `EmailStr` do Pydantic → `ImportError` no arranque.
4. Healthcheck do backend usava `curl`, ausente em `python:3.11-slim`.
5. `SECRET_KEY` vazio em `ENVIRONMENT=production`; o guard de segurança
   rejeitava o default de desenvolvimento (e, antes, aceitava uma chave vazia).

## Alterações

- `docker-compose.yml`
  - Postgres passou a `POSTGRES_USER/PASSWORD/DB` com defaults; healthcheck alinhado.
  - `command: ["postgres", "-c", "shared_preload_libraries=pg_stat_statements"]`.
  - Healthcheck do backend passou a `python -c "urllib.request.urlopen(...)"`.
  - `SECRET_KEY` com fallback explícito ao default de desenvolvimento (falha
    fechada em produção, em vez de aceitar chave vazia).
  - Removida a chave obsoleta `version:`.
- `backend/requirements.txt`: `pydantic[email]`.
- `Makefile`: `start` gera `.env` (gitignored) com `SECRET_KEY` aleatório
  quando ausente.

## Critérios de aceitação

- [x] `make start` termina com código 0.
- [x] `postgres` healthy.
- [x] `backend` healthy; `GET /health` → 200; `GET /docs` → 200.
- [x] `frontend` up; `GET /` → 200.
- [x] Nenhum secret real versionado (`.env` está no `.gitignore`).

## Fora de âmbito

- Prefixo `/api` no proxy Nginx vs rotas do backend (não afeta `make start`).
- Migração de `secrets/*.txt` para um gestor de segredos.
- Testes E2E completos (requerem dados de seed).

## Rollback

Reverter os três ficheiros alterados e `docker compose down -v`.
