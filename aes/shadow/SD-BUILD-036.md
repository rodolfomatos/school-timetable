# Shadow Doc SD-BUILD-036 — T049 Fase 2: Integridade do modelo SQLAlchemy

## Proveniência
Fase 2 do plano de auditoria AES T047–T059, concluída em 31/10/2026 sobre o
commit de partida `bacb75e`.

## Objetivo
Restabelecer a integridade do grafo de relações SQLAlchemy para que
`configure_mappers()` e qualquer operação CRUD fossem possíveis.

## Decisões tomadas
- Manter a nomenclatura inglesa já usada pelo contrato público (`Room`,
  `Subject`, `Class`, `capacity`, `weekly_load`, `student_count`), porque
  routers e schemas Pydantic dependem dela.
- Restaurar os modelos a partir do `HEAD` em vez de continuar a corrigir por
  `sed`; as reescritas anteriores tinham introduzido nomes portugueses
  incompatíveis (`Sala`, `Disciplina`, `nome`, `capacidade`).
- Corrigir apenas as cinco relações realmente defeituosas.
- Testar com SQLite assíncrono em memória, com `selectinload` explícito para
  evitar `MissingGreenlet` em SQLAlchemy async.
- Provar a regressão num worktree limpo: o mesmo teste falhava no `HEAD`.

## Causa-raiz
- Auto-referência em `ScheduleVersion.assignments`.
- `ScheduleAssignment.class_` mapeado para `Course` em vez de `Class`.
- `Course.subjects` inexistente apesar de `Subject.course` o exigir.
- Relações `unavailabilities`/`disputes` declaradas em `User` mas pertencentes
  a `Teacher`.
- Import `TYPE_CHECKING` a apontar para o módulo errado.

## Evidência
- `configure_mappers()` → `MAPPERS_OK`, 10 tabelas registadas.
- `backend/tests/test_models_crud.py`: 2 passed (2 failed no `HEAD`).
- `from app.main import app` → `APP_IMPORT_OK 14`.
- `ruff` → `All checks passed!`.
- Suite canónica → 90.59% de cobertura.

## Escore epistémico
Alta confiança — defeito reproduzido, correcção mínima, teste que falha antes e
passa depois, e validação independente do import da aplicação.

## Próximos passos
- T050: autenticação e privilégios (registo público sempre `student`,
  remover `resolved_by = 1`, hardening de cookies/CSRF).
