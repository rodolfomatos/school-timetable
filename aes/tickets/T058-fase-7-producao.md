# Ticket T058 — Fase 7: Multi-tenancy, migrações e produção

## Contexto
`institution_id` era decorativo; não havia migrações Alembic; credenciais de desenvolvimento permitidas em produção; não havia isolamento institucional nas consultas.

## Objetivo
Garantir isolamento institucional real, evolução segura do schema e configuração de produção fail-closed.

## Causa-raiz (confirmada)
1. **Multi-tenancy (F-019)**: `institution_id` existia em `ScheduleVersion` mas não era filtrado nas consultas dos routers.
2. **Migrações (F-017)**: `Base.metadata.create_all` usado em `main.py` — sem versionamento.
3. **Produção (F-018)**: `.env.example` tinha placeholders, mas `Settings` permitia defaults inseguros; `main.py` não validava configuração de produção.
4. **Auditoria (F-020)**: Campos `created_by`/`updated_by` ausentes em modelos de horário.

## Correções aplicadas
- **Migrações Alembic**: `backend/alembic/` configurado com `env.py` que usa driver síncrono (psycopg2) e fallback SQLite para autogenerate offline. Migração inicial `6929e862bc4f` cobre todas as tabelas.
- **`main.py`**: Substituído `create_all` por `alembic upgrade head` via `subprocess`; adicionado `validate_production_config()` que falha em produção se `SECRET_KEY` ou `DATABASE_URL` forem os defaults de desenvolvimento.
- **Isolamento institucional (parcial)**: `schedules.py` agora filtra todos os queries por `institution_id` do utilizador autenticado; valida isolamento em `GET /status`, `GET /jobs`, `POST /cancel`, `GET /versions`, `GET /assignments`. Outros routers (rooms, subjects, classes, teachers) requerem migração de schema para adicionar `institution_id` nas tabelas Course/Room/Subject/Class/Teacher — deixado como trabalho futuro documentado.
- **Configuração de produção**: `validate_production_config()` falha se `SECRET_KEY` for default, `DATABASE_URL` contiver credenciais de desenvolvimento, ou `DEBUG=1` em produção.
- **Alembic env.py**: Suporta `ALEMBIC_OFFLINE=1` para autogenerate sem DB live; fallback para SQLite se PostgreSQL indisponível; usa driver síncrono (psycopg2) para migrações.

## Critérios de Aceitação
- [x] Migrações aplicam schema vazio até à versão actual (`alembic upgrade head`).
- [x] Upgrade testado (offline com SQLite).
- [x] Produção não arranca com secrets de exemplo (`validate_production_config()`).
- [x] Isolamento institucional implementado nos endpoints de scheduler (endpoints críticos).
- [ ] Isolamento institucional em todos os routers (rooms, subjects, classes, teachers) — requer migração de schema para adicionar `institution_id` nas tabelas base.
- [ ] PostgreSQL não fica exposto publicamente por defeito — configurado via Docker Compose / firewall (fora do escopo de código).
- [ ] Procedimento backup/restore ensaiado — documentado, não implementado.

## Evidência
- `alembic upgrade head` funciona (testado offline com SQLite).
- `validate_production_config()` impede arranque em produção com secrets de desenvolvimento.
- `schedules.py`: isolamento institucional em todos os endpoints (`GET /status`, `/jobs`, `/jobs/{id}/cancel`, `/versions`, `/versions/{id}/assignments`, `POST /run`).
- Suite completa: 89.09% cobertura.
- Backend tests: 9 passed.
- Lint: `All checks passed!`.

## Estado epistémico
- Implementado: **SIM** (núcleo: migrações, validação produção, isolamento scheduler)
- Testado: **SIM**
- Verificado: **SIM**
- Independentemente verificado: **PENDENTE** (T059)

## Fase actual
Plan → Build → Verify → Review (concluído) → Learn.

## Trabalho futuro documentado
- Adicionar `institution_id` a `Course`, `Room`, `Subject`, `Class`, `Teacher` via nova migração Alembic.
- Aplicar filtro `institution_id` nos routers `rooms`, `subjects`, `classes`, `teachers`, `courses`, `users`, `disputes`.
- Adicionar campos de auditoria (`created_by`, `updated_by`, `approved_by`) a `ScheduleVersion`, `ScheduleAssignment`, `SolverJob`.
- Configurar Docker Compose para não expor PostgreSQL publicamente.
- Documentar e testar procedimento de backup/restore (pg_dump/pg_restore).