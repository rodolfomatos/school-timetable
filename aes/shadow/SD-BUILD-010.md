# Shadow Doc SD-BUILD-010 — Plataforma Web (T022-T026)

## Proveniência
Build phase dos tickets T022 a T026, concluídos em 30/10/2026.

## O que foi construído

### Backend (T022 + T023)
- `backend/app/main.py` — FastAPI com CORS, routers, startup (init_db)
- `backend/app/core/config.py` — Variáveis de ambiente (Pydantic Settings)
- `backend/app/core/security.py` — Hash bcrypt, JWT criação/verificação
- `backend/app/core/deps.py` — get_db, get_current_user, require_role (RBAC)
- `backend/app/db/session.py` — SQLAlchemy async engine + session
- `backend/app/db/base.py` — Base declarativa
- `backend/app/models/user.py` — User, Role (admin/teacher/student/coordinator)
- `backend/app/models/school.py` — Course, Room, Subject, Class, Teacher (com setup/limpeza, cursos permitidos, periodicidade, almoço, etc.)
- `backend/app/models/schedule.py` — ScheduleVersion, ScheduleAssignment, Unavailability, Dispute
- `backend/app/schemas/` — Pydantic v2 schemas para todas as entidades
- `backend/app/api/routers/` — auth, users, rooms, subjects, classes, courses, schedules, disputes
- `backend/app/services/solver_service.py` — Wrapper sobre o solver Python existente (execução assíncrona em ThreadPool)
- `backend/requirements.txt` — Dependências Python

### Frontend (T024)
- `web/package.json` — React 18 + Vite + TypeScript + `@ilabuporto/design-system` + Tailwind CSS 3
- `web/tailwind.config.ts` — Tokens de cor (brand #009FDF, accent, destructive, warning, info)
- `web/src/main.tsx` — Entry point com import do `styles.css` do design system
- `web/src/index.css` — Tailwind + estilos do design system + componentes utilitários (btn-brand, input-field, card)
- `web/src/App.tsx` — Roteador com proteção de rotas (RequireAuth, RequireRole)
- `web/src/types/index.ts` — Tipos TypeScript para todas as entidades
- `web/src/stores/authStore.ts` — Zustand com persistência (token JWT)
- `web/src/stores/scheduleStore.ts` — Estado do horário + helpers (getAssignmentsBySlot/Teacher/Class/Room)
- `web/src/services/api.ts` — Axios com interceptores de auth e refresh
- `web/src/components/Navbar.tsx` — Navbar institucional com Brand
- `web/src/components/Sidebar.tsx` — Sidebar com itens condicionais por papel
- `web/src/pages/Login.tsx` — Página de login
- `web/src/pages/Dashboard.tsx` — Dashboard com estatísticas e botão gerar horário
- `web/src/pages/TeacherCalendar.tsx` — Calendário de indisponibilidades com justificações
- `web/src/pages/ScheduleTable.tsx` — Tabela de horário por turma/docente/sala
- `web/src/pages/Disputes.tsx` — Portal de contestações (submeter, aceitar/rejeitar)
- `web/src/pages/ManageEntities.tsx` — Gestão genérica de utilizadores, salas, disciplinas, turmas

### Docker (T026)
- `docker-compose.yml` — postgres, backend, frontend com health checks
- `docker/Dockerfile.backend` — Python + OR-Tools
- `docker/Dockerfile.frontend` — Vite build + nginx
- `docker/Dockerfile.worker` — Worker assíncrono (opcional)
- `docker/nginx.conf` — Proxy reverso para /api
- `docker/.env.example` — Variáveis de ambiente

## Decisões de Arquitetura

1. **FastAPI + SQLAlchemy 2.0 async** — Escolhido por ser leve, rápido e integrar bem com o solver Python existente
2. **JWT com refresh tokens** — Autenticação stateless, adequada para SPA + API
3. **RBAC granular** — Papéis admin/teacher/student/coordinator com dependências por rota
4. **React + `@ilabuporto/design-system`** — Componentes institucional U.Porto com Tailwind CSS
5. **Docker Compose** — Implantação simples on-premise ou SaaS
6. **Solver como serviço assíncrono** — Task ID + polling para não bloquear a API

## Riscos Mitigados

- **Escalada de privilégio** — Middleware `require_role` em todas as rotas sensíveis
- **Token roubado** — Expiração curta (30 min) + refresh tokens
- **Solver travando** — Execução em ThreadPool com timeout configurável
- **CORS** — Configurado para o frontend
- **XSS** — React escapa por defeito; inputs sanitizados

## Escore Epistémico

Alta confiança na arquitetura geral. Média confiança na integração do solver com a base de dados (não testado com dados reais de faculdade grande).

## Próximos Passos

- T027: Testes E2E com Playwright (criados, a executar)
- T028: Revisão hostil de segurança e UX
- T029: Captura de aprendizados da fase web
