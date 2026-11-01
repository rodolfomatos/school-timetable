# Shadow Doc SD-BUILD-045 — T058 Fase 7: Multi-tenancy, migrações e produção

## Proveniência
Fase 7 do plano de auditoria AES T047–T059, concluída em 01/11/2026 sobre o
commit `6a74810` (T057 incluído).

## Objetivo
Garantir isolamento institucional real, evolução segura do schema via Alembic,
e configuração de produção fail-closed.

## Decisões tomadas
- **Alembic**: Configurado em `backend/alembic/` com `env.py` que usa driver
  síncrono (psycopg2) para migrações, fallback SQLite para autogenerate offline
  (`ALEMBIC_OFFLINE=1`), e usa URL síncrona derivada de `DATABASE_URL`.
- **Migração inicial**: `6929e862bc4f` cobre todas as tabelas (users, courses,
  rooms, subjects, classes, teachers, schedule_versions, schedule_assignments,
  unavailabilities, disputes, class_subjects, teacher_subjects, solver_jobs).
- **`main.py`**: Substituído `Base.metadata.create_all` por `alembic upgrade head`
  executado via `subprocess` no arranque; adicionado `validate_production_config()`
  que falha em produção se `SECRET_KEY` for default, `DATABASE_URL` usar
  credenciais de dev, ou `DEBUG=1`.
- **Isolamento institucional**: Implementado em `schedules.py` (endpoints
  críticos de solver) — todos os endpoints filtram por `institution_id` do
  utilizador autenticado; validação de acesso cross-institution.
- **Configuração de produção**: `.env.example` com placeholders;
  `validate_production_config()` falha em produção se `SECRET_KEY` for default,
  `DATABASE_URL` usar credenciais de dev, ou `DEBUG=1`.
- **Alembic env.py**: Suporta `ALEMBIC_OFFLINE=1` para autogenerate sem DB live;
  fallback para SQLite se PostgreSQL indisponível; usa driver síncrono (psycopg2).

## Limitações conhecidas (trabalho futuro)
- Isolamento institucional incompleto: routers `rooms`, `subjects`, `classes`,
  `teachers`, `courses`, `users`, `disputes` não filtram por `institution_id`.
  Requer adicionar coluna `institution_id` a `Course`, `Room`, `Subject`,
  `Class`, `Teacher`, `User` via nova migração Alembic.
- Campos de auditoria (`created_by`, `updated_by`, `approved_by`) ausentes em
  `ScheduleVersion`, `ScheduleAssignment`, `SolverJob`.
- Backup/restore não automatizado/testado.
- PostgreSQL exposto por defeito no Docker Compose (requer configuração de rede/firewall).

## Evidência
- `alembic upgrade head` funciona (testado offline com SQLite).
- `validate_production_config()` impede arranque em produção com secrets de desenvolvimento.
- `schedules.py`: isolamento institucional em todos os endpoints (`GET /status`,
  `/jobs`, `/jobs/{id}/cancel`, `/versions`, `/versions/{id}/assignments`,
  `POST /run`).
- Suite completa: 89.09% cobertura.
- Backend tests: 9 passed.
- Lint: `All checks passed!`.

## Escore epistémico
Alta confiança para o núcleo implementado (migrações, validação produção,
isolamento scheduler). Confiança média para isolamento completo — requer
migração de schema adicional.

## Próximos passos
- T059: Verificação epistemológica final.