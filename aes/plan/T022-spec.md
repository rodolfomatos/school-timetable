# AES Plan Spec — T022 Backend API FastAPI

## 1. Sumário Executivo
API REST FastAPI que expõe o solver Python existente, com autenticação JWT, RBAC e CRUD de entidades. Serve o frontend React.

## 2. Stack
- Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, python-jose[cryptography], passlib[bcrypt], python-multipart
- Pydantic v2 para schemas
- Uvicorn para servir

## 3. Estrutura de Diretórios
```
backend/
  app/
    main.py              # FastAPI app, routers, lifespan
    core/
      config.py          # Variáveis de ambiente (SECRET_KEY, DATABASE_URL, etc.)
      security.py        # JWT criação/verificação, hash de senhas
      deps.py            # Dependiências: get_db, get_current_user, role checks
    db/
      session.py         # Engine, SessionLocal, Base
      base.py            # SQLAlchemy declarative base
    models/              # Modelos SQLAlchemy
      user.py, school.py, schedule.py, dispute.py
    schemas/             # Schemas Pydantic
      user.py, school.py, schedule.py, dispute.py, token.py
    api/
      routers/
        auth.py          # /auth/register, /auth/login, /auth/refresh
        users.py         # CRUD utilizadores
        schools.py       # CRUD salas, disciplinas, turmas, cursos
        schedules.py     # /solver/run, /schedule/versions
        disputes.py      # /disputes (CRUD + aceitar/rejeitar)
    services/
      solver_service.py  # Wrapper sobre o solver Python existente
```

## 4. Endpoints
- `POST /auth/register` → cria utilizador (apenas admin pode criar admin)
- `POST /auth/login` → JWT access + refresh tokens
- `POST /auth/refresh` → novo access token
- `GET /users/me` → perfil do utilizador autenticado
- `GET /users` (admin) → listar utilizadores
- `POST /schools/rooms`, `GET /schools/rooms`, `PUT/DELETE /schools/rooms/{id}`
- `POST /schools/courses`, `GET /schools/courses`, ...
- `POST /schools/subjects`, `GET /schools/subjects`, ...
- `POST /schools/classes`, `GET /schools/classes`, ...
- `POST /solver/run` → executa solver assíncrono, devolve task_id
- `GET /solver/status/{task_id}` → estado da tarefa
- `GET /schedule/versions` → listar versões de horário
- `POST /disputes` (docente) → submeter contestação
- `GET /disputes` (admin) → listar pendentes
- `PATCH /disputes/{id}` (admin) → aceitar/rejeitar

## 5. Modelos de Dados (SQLAlchemy)
- User: id, email, hashed_password, role, institution_id, created_at
- Room: id, name, capacity, room_type, allowed_courses, reserved_times, setup_before, cleanup_after
- Subject: id, name, weekly_load, periodicity, room_type_required, weeks_active
- Class: id, name, course, year, student_count, weeks_active
- Teacher: id, user_id, availability (JSON), day_off_preferred, morning_preferred, lunch_sacred, commute_time
- ScheduleVersion: id, status (draft/published/archived), created_at, solver_used, score
- ScheduleAssignment: id, version_id, class_id, subject_id, teacher_id, room_id, slot (JSON)
- Unavailability: id, teacher_id, slot (JSON), justification
- Dispute: id, teacher_id, assignment_id, reason, justification, status (pending/accepted/rejected), created_at, resolved_at

## 6. Solver Service
- Wrapper sobre `src/timetable/` do projeto existente
- Converte modelos SQLAlchemy → modelos do solver → executa → converte resultado de volta
- Execução assíncrona com `asyncio` + `concurrent.futures` para não bloquear a API
- Timeout configurável (default 60s)

## 7. Testes
- `backend/tests/test_auth.py` — registro, login, refresh, tokens expirados
- `backend/tests/test_rooms.py` — CRUD salas
- `backend/tests/test_scheduler.py` — execução do solver com dados pequenos
- `backend/tests/test_disputes.py` — criar, listar, aceitar/rejeitar contestações
- Cobertura ≥ 80%

## 8. Quality Gates
- `make test` passa (pytest + coverage)
- `make lint` passa (ruff)
- `make typecheck` passa (mypy)
