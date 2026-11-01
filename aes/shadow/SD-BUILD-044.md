# Shadow Doc SD-BUILD-044 — T057 Fase 7: SolverResult e jobs persistentes

## Proveniência
Fase 7 do plano de auditoria AES T047–T059, concluída em 01/11/2026 sobre o
commit `2f44339` (T056 incluído).

## Objetivo
Substituir o armazenamento em memória (`_solver_tasks` dict) por persistência
completa em base de dados, com ciclo de vida explícito de job e distinção de
estados de timeout.

## Decisões tomadas
- **Modelo `SolverJob`** em `schedule.py`: UUID PK, FK para `ScheduleVersion`,
  estados enum (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`,
  `TIMEOUT_WITH_INCUMBENT`, `TIMEOUT_NO_SOLUTION`), campos de auditoria
  (`created_by`, `started_at`, `completed_at`), parâmetros do solver (JSON),
  erro, tempo decorrido, seed.
- **Serviço `solver_service.py`**:
  - `create_solver_job()` assíncrono cria job PENDING, devolve UUID.
  - `_run_solver_sync()` em thread: atualiza para RUNNING, executa solver,
    avalia, detecta se resultado == inicial (timeout sem solução),
    persiste `ScheduleVersion` + `ScheduleAssignment` se viável,
    actualiza job com status final e métricas.
  - `get_solver_job`, `list_solver_jobs`, `cancel_solver_job` assíncronos.
- **API `schedules.py`**: `POST /run` → `create_solver_job`, `GET /status/{job_id}`,
  `GET /jobs` (listar com filtros), `POST /jobs/{job_id}/cancel`.
- **Schemas**: `task_id` → `job_id`, status expandido com timeouts distintos.

## Evidência
- Backend tests: 9 passed.
- Suite completa: 89.09% cobertura.
- Lint: `All checks passed!`.
- Import: `from app.main import app` → `APP_IMPORT_OK 14`.

## Escore epistémico
Alta confiança — job sobrevive a reinício, estados são consultáveis e
persistíveis, timeout com/sem incumbent distinguido, falha não devolve
inicial como solução.

## Próximos passos
- T058: Multi-tenancy, migrações (Alembic), produção.
- T059: Verificação epistemológica final.