# Ticket T057 — Fase 7: SolverResult e jobs persistentes

## Contexto
O resultado do solver não era guardado; tarefas existiam apenas em memória
(`_solver_tasks` dict); não havia persistência de `ScheduleVersion`/`ScheduleAssignment`.
Estados não sobreviviam a reinício, não eram consultáveis por utilizador autorizado,
e não se distinguia timeout com incumbent válido de timeout sem solução.

## Objetivo
Introduzir um contrato explícito de resultado (`SolverJob`) e um ciclo de vida durável
para execuções do solver, com persistência completa em base de dados.

## Causa-raiz (confirmada)
1. `backend/app/services/solver_service.py` usava `_solver_tasks: dict[str, dict]`
   em memória — perdia tudo no reinício.
2. Não havia modelo `SolverJob` na base de dados.
3. `create_solver_task`/`get_solver_task` operavam só no dict em memória.
4. `ScheduleVersion`/`ScheduleAssignment` nunca eram persistidos após solver.
5. Não se distinguia timeout com incumbent válido de timeout sem solução.
6. Falha devolvia horário inicial como se fosse resultado calculado.

## Correções aplicadas
- **`backend/app/models/schedule.py`**: Novo modelo `SolverJob` com campos:
  - `id` (UUID), `institution_id`, `status` (pending/running/completed/failed/cancelled/timeout_with_incumbent/timeout_no_solution)
  - `solver`, `time_limit_seconds`, `additional_unavailabilities`, `schedule_version_id` (FK)
  - `score`, `hard_violations`, `soft_penalties`, `error`, `elapsed_seconds`, `seed`, `solver_params`
  - `created_by`, `created_at`, `started_at`, `completed_at`
  - Relações com `ScheduleVersion` e `User`
- **`backend/app/services/solver_service.py`**:
  - `create_solver_job()`: cria `SolverJob` PENDING na BD, devolve UUID
  - `_run_solver_sync()`: executa em thread, atualiza job para RUNNING, executa solver,
    persiste `ScheduleVersion` + `ScheduleAssignment` se viável,
    distingue `COMPLETED` / `TIMEOUT_WITH_INCUMBENT` / `TIMEOUT_NO_SOLUTION` / `FAILED`
  - `get_solver_job()`, `list_solver_jobs()`, `cancel_solver_job()`: operações assíncronas
- **`backend/app/api/routers/schedules.py`**: Endpoints actualizados
  - `POST /scheduler/run` → `create_solver_job` (devolve `job_id`)
  - `GET /scheduler/status/{job_id}` → `get_solver_job`
  - `GET /scheduler/jobs` → listar com filtros
  - `POST /scheduler/jobs/{job_id}/cancel` → cancelar PENDING/RUNNING
- **`backend/app/schemas/schedule.py`**: `task_id` → `job_id`, status expandido

## Critérios de Aceitação
- [x] Job sobrevive a reinício do processo (persistido em BD).
- [x] Estados são consultáveis por utilizador autorizado (endpoints autenticados).
- [x] Timeout com incumbent válido distinguido de timeout sem solução
  (`COMPLETED`/`TIMEOUT_WITH_INCUMBENT` vs `TIMEOUT_NO_SOLUTION`).
- [x] Falha não devolve horário inicial como resultado calculado
  (detecta `resultado_e_inicial` e marca `TIMEOUT_NO_SOLUTION`).
- [x] Solução persistida passa no validador independente (reutiliza `avaliar`).
- [x] Versão e atribuições consultáveis após nova sessão DB (`ScheduleVersion` + `ScheduleAssignment`).
- [x] Cancelamento e falha ficam registados (status `CANCELLED`/`FAILED`).

## Evidência
- Backend tests: 9 passed.
- Suite completa: 89.09% cobertura.
- Lint: `All checks passed!`.
- Import: `from app.main import app` → `APP_IMPORT_OK 14`.

## Estado epistémico
- Implementado: **SIM**
- Testado: **SIM**
- Verificado: **SIM**
- Independentemente verificado: **PENDENTE** (T059)

## Fase actual
Plan → Build → Verify → Review (concluído) → Learn.