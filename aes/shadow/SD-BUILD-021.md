# Shadow Doc SD-BUILD-021 — Fase 7: Backend e Operação (T043)

## Proveniência
Fase 7 do plano de auditoria (DOCX seção 11), concluída em 31/10/2026.

## O que foi construído

### Backend FastAPI
- `main.py`: Aplicação com CORS, routers, startup (init_db)
- `core/config.py`: Variáveis de ambiente via Pydantic Settings
- `core/security.py`: Hash bcrypt, JWT criação/verificação
- `core/deps.py`: get_db, get_current_user (cookie httpOnly), require_role (RBAC)
- `db/session.py`: SQLAlchemy async engine + session
- `db/base.py`: Base declarativa
- `models/`: User, Role, Course, Room, Subject, Class, Teacher, ScheduleVersion, ScheduleAssignment, Unavailability, Dispute
- `schemas/`: Pydantic v2 para todas as entidades
- `api/routers/`: auth, users, rooms, subjects, classes, courses, schedules, disputes
- `services/solver_service.py`: Wrapper sobre solver Python (execução em ThreadPool)

### Decisões de arquitetura
- FastAPI + SQLAlchemy 2.0 async (leve, rápido, integra com solver Python)
- JWT com refresh tokens (autenticação stateless)
- RBAC com papéis admin/teacher/student/coordinator
- CP-SAT executado em ThreadPool para não bloquear a API
- Fallback graceful se ortools não disponível

## Escore epistémico
Alta confiança na arquitetura geral. Média confiança na integração completa (backend + solver) sem teste de deploy completo.

## Próximos passos
- T044: Testes e benchmarks
- T045: Entregáveis finais
