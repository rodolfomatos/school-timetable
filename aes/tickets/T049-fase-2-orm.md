# Ticket T049 — Fase 2: Integridade do modelo SQLAlchemy

## Contexto
`configure_mappers()` falhava, impedindo qualquer operação real sobre a base de
dados. O defeito era composto por relações assimétricas entre `User`, `Teacher`,
`Course`, `Subject` e `ScheduleAssignment`.

## Objetivo
Corrigir e validar integralmente o grafo de entidades e relações SQLAlchemy, sem
alterar contratos públicos da API.

## Causa-raiz (confirmada em HEAD `bacb75e`)
1. `ScheduleVersion.assignments` apontava para `"ScheduleVersion"` em vez de
   `"ScheduleAssignment"`, com `back_populates="assignments"` (auto-referência
   inválida).
2. `ScheduleAssignment.class_` estava mapeado como `Course`, embora a FK
   `class_id` referencie `classes.id`; `Course` também não possui `assignments`.
3. `Course` não declarava `subjects`, apesar de `Subject.course` usar
   `back_populates="subjects"`.
4. `User` declarava `unavailabilities` e `disputes` com
   `back_populates="teacher"`, mas essas relações pertencem a `Teacher`; em
   `User` geravam `KeyError: 'teacher'`.
5. O import de tipos em `school.py` sob `TYPE_CHECKING` apontava
   `Unavailability`/`Dispute` para o próprio módulo `school`, onde não existem.

## Correções aplicadas
- `backend/app/models/schedule.py`: alvo correcto de `ScheduleVersion.assignments`;
  `class_` mapeado para `Class`; import de `Class` em vez de `Course`.
- `backend/app/models/school.py`: adicionada a relação inversa `Course.subjects`;
  corrigido o import `TYPE_CHECKING` para `app.models.schedule`.
- `backend/app/models/user.py`: removidas as relações duplicadas/incorrectas;
  `User.teacher_profile` mantém-se como única relação com `Teacher`.
- `backend/tests/test_models_crud.py`: teste de integridade + CRUD relacional
  assíncrono sobre SQLite em memória.
- `backend/pytest.ini`: `asyncio_mode = auto` e `testpaths = tests`.

## Critérios de Aceitação
- [x] `configure_mappers()` executa sem excepções.
- [x] Teste cria, consulta, actualiza e elimina entidades relacionadas numa BD de teste.
- [x] Não existem `NoForeignKeysError`, `InvalidRequestError` ou warnings relevantes de mapper.
- [x] Relações e cascades estão documentadas (ver tabela abaixo).
- [x] Testes cobrem as cardinalidades e integridade referencial.

## Relações e cascades
| Relação | Cardinalidade | Cascade |
|---|---|---|
| `Course.rooms` ↔ `Room.course` | 1:N | — |
| `Course.subjects` ↔ `Subject.course` | 1:N | — |
| `Course.classes` ↔ `Class.course` | 1:N | — |
| `User.teacher_profile` ↔ `Teacher.user` | 1:1 | `all, delete-orphan` |
| `Teacher.unavailabilities` ↔ `Unavailability.teacher` | 1:N | `all, delete-orphan` |
| `Teacher.disputes` ↔ `Dispute.teacher` | 1:N | `all, delete-orphan` |
| `Teacher.assignments` ↔ `ScheduleAssignment.teacher` | 1:N | — |
| `Room.assignments` ↔ `ScheduleAssignment.room` | 1:N | — |
| `Subject.assignments` ↔ `ScheduleAssignment.subject` | 1:N | — |
| `Class.assignments` ↔ `ScheduleAssignment.class_` | 1:N | — |
| `ScheduleVersion.assignments` ↔ `ScheduleAssignment.version` | 1:N | `all, delete-orphan` |
| `ScheduleAssignment.disputes` ↔ `Dispute.assignment` | 1:N | `all, delete-orphan` |
| `Dispute.resolver` → `User` | N:1 | — |

## Evidência de regressão
- Antes da correcção (worktree limpo em `bacb75e`, com o mesmo teste):
  `2 failed` — `InvalidRequestError: Mapper[Course(courses)] has no property 'subjects'`.
- Depois da correcção: `2 passed`.
- `PYTHONPATH=. python3 -c "from app.main import app"` → `APP_IMPORT_OK 14`.
- `ruff check src tests backend/app backend/tests` → `All checks passed!`.
- Suite canónica: 90.59% de cobertura, sem falhas.

## Estado epistémico
- Implementado: **SIM**
- Testado: **SIM**
- Verificado: **SIM** (execução real em SQLite + import da app)
- Independentemente verificado: **PENDENTE** (T059)

## Fase atual
Plan → Build → Verify → Review (concluído) → Learn.
