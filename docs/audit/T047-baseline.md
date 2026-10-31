# Shadow Doc SD-BUILD-035 — T047 Fase 0: Baseline e Verificação Independente

## Proveniência
Fase 0 do plano de auditoria AES T047–T059, executada em 31/10/2026.

## Objetivo
Estabelecer uma baseline reproduzível e verificar independentemente o estado real do código, testes, documentação e tickets T036–T046. Nenhuma alteração de código foi feita nesta fase.

## Ambiente de Execução

| Item | Versão |
|------|--------|
| Python | 3.10.12 |
| Node.js | v24.18.0 |
| OR-Tools | 9.15.6755 |
| FastAPI | 0.138.0 |
| SQLAlchemy | 2.0.51 |
| Hypothesis | 6.168.5 |
| pytest | 9.1.1 |
| ruff | 0.15.20 |
| mypy | 2.1.0 |
| Playwright | 1.40.0 (e2e/) |
| Vitest | 1.6.1 (web/) |

## Comandos de Teste

| Comando | Propósito | Status |
|---------|-----------|--------|
| `PYTHONPATH=src python3 -m pytest tests/ --cov=src/timetable` | Testes Python do solver | ✅ Passa (90.61% cobertura) |
| `ruff check src tests` | Lint Python | ✅ Passa (0 erros) |
| `ruff format --check src tests` | Formatação Python | ✅ Passa |
| `cd backend && python3 -m pytest tests/` | Testes backend FastAPI | ⚠️ Nenhum teste encontrado |
| `cd web && npm test` | Testes frontend Vitest | ⚠️ Nenhum arquivo de teste encontrado |
| `cd e2e && npx playwright test` | Testes E2E Playwright | ⚠️ Não executado (requer servidor ativo) |

## Estrutura do Repositório

### `src/timetable/` — Núcleo do Solver Python

| Módulo | Responsabilidade | Linhas | Cobertura | Status |
|--------|-----------------|--------|-----------|--------|
| `models.py` | Slot, Sala, Professor, Turma, Disciplina, Aula, Horario, RelacaoCasamento, RelacaoFilho, Subgrupo | 104 | 90% | Implementado |
| `constraints.py` | Restrições duras H01-H08 e moles S01-S10 (adiitivas) | 158 | 96% | Implementado |
| `objective.py` | Função objetivo aditiva: score = -Σ(penalidade × peso) | 32 | 100% | Implementado |
| `seed.py` | Geração de seed parcial imutável (~30% dos slots) | 45 | 62% | Esqueleto |
| `solver.py` | Interface abstrata SolverBase | 8 | 0% | Esqueleto |
| `cp_sat_baseline.py` | Wrapper OR-Tools CP-SAT (opcional) | 264 | 93% | Implementado |
| `local_search.py` | Tabu Search e Simulated Annealing | 134 | 91% | Implementado |
| `ui.py` | Exportação/importação JSON (insets de plástico) | 85 | 88% | Esqueleto |
| `export.py` | Exportação CSV e iCal (.ics) | 51 | 100% | Implementado |

**Total statements: 882 | Missing: 83 | Cobertura: 90.61%**

### `backend/` — API FastAPI

| Módulo | Responsabilidade | Status |
|--------|-----------------|--------|
| `app/main.py` | Aplicação FastAPI, routers, CORS, startup init_db | Implementado |
| `app/core/config.py` | Configurações via Pydantic Settings | Implementado |
| `app/core/security.py` | Hash bcrypt, JWT criação/verificação, decode | Implementado |
| `app/core/deps.py` | get_db, get_current_user (cookie httpOnly), require_role | Implementado |
| `app/db/session.py` | SQLAlchemy async engine + session | Implementado |
| `app/models/user.py` | User, Role (admin/teacher/student/coordinator) | Implementado |
| `app/models/school.py` | Course, Room, Subject, Class, Teacher (alargado) | Implementado |
| `app/models/schedule.py` | ScheduleVersion, ScheduleAssignment, Unavailability, Dispute | Implementado |
| `app/schemas/user.py` | Schemas Pydantic para utilizadores | Implementado |
| `app/schemas/school.py` | Schemas Pydantic para entidades da escola | Implementado |
| `app/schemas/schedule.py` | Schemas Pydantic para horários, disputas | Implementado |
| `app/api/routers/auth.py` | /auth/register, /auth/login, /auth/refresh, /auth/logout | Implementado |
| `app/api/routers/users.py` | CRUD utilizadores | Implementado |
| `app/api/routers/rooms.py` | CRUD salas | Implementado |
| `app/api/routers/subjects.py` | CRUD disciplinas | Implementado |
| `app/api/routers/classes.py` | CRUD turmas | Implementado |
| `app/api/routers/courses.py` | CRUD cursos | Implementado |
| `app/api/routers/schedules.py` | /scheduler/run, /scheduler/status/{task_id}, /schedule/versions | Implementado |
| `app/api/routers/disputes.py` | /disputes (criar, listar, aceitar/rejeitar) | Implementado |
| `app/services/solver_service.py` | Wrapper sobre solver Python (execução em ThreadPool) | Implementado |
| `backend/requirements.txt` | Dependências Python | Implementado |

### `web/` — Frontend React

| Módulo | Responsabilidade | Status |
|--------|-----------------|--------|
| `src/App.tsx` | Roteador com proteção de rotas | Implementado |
| `src/components/Navbar.tsx` | Navbar institucional | Implementado |
| `src/components/Sidebar.tsx` | Sidebar com itens condicionais por papel | Implementado |
| `src/pages/Login.tsx` | Página de login | Implementado |
| `web/src/pages/Dashboard.tsx` | Dashboard com estatísticas | Implementado |
| `src/pages/TeacherCalendar.tsx` | Calendário de indisponibilidades | Implementado |
| `src/pages/ScheduleTable.tsx` | Tabela de horário | Implementado |
| `src/pages/Disputes.tsx` | Portal de contestações | Implementado |
| `src/pages/ManageEntities.tsx` | Gestão de entidades | Implementado |
| `web/src/services/api.ts` | Axios com interceptores de auth | Implementado |
| `web/src/stores/authStore.ts` | Estado de autenticação | Implementado |
| `web/src/stores/scheduleStore.ts` | Estado do horário | Implementado |
| `web/src/types/index.ts` | Tipos TypeScript | Implementado |
| `web/src/utils/sanitize.ts` | Sanitização JSON com DOMPurify | Implementado |

### `docker/` e `docker-compose.yml` — Implantação

| Arquivo | Responsabilidade | Status |
|---------|-----------------|--------|
| `docker-compose.yml` | Orquestração postgres + backend + frontend | Implementado |
| `docker/Dockerfile.backend` | Python + OR-Tools | Implementado |
| `docker/Dockerfile.frontend` | Vite build + nginx | Implementado |
| `docker/Dockerfile.worker` | Worker assíncrono (opcional) | Implementado |
| `docker/nginx.conf` | Proxy reverso para /api | Implementado |
| `docker/.env.example` | Placeholders (sem credenciais reais) | Implementado |

### `e2e/` — Testes Playwright

| Arquivo | Responsabilidade | Status |
|---------|-----------------|--------|
| `e2e/playwright.config.ts` | Configuração Playwright | Implementado |
| `e2e/tests/teacher-calendar.spec.ts` | Docente marca indisponibilidade | Implementado |
| `e2e/tests/admin-generate.spec.ts` | Admin gera horário | Implementado |
| `e2e/tests/disputes.spec.ts` | Docente contesta slot | Implementado |
| `e2e/tests/accessibility.spec.ts` | Navegação por teclado, contraste | Implementado |
| `e2e/tests/mobile.spec.ts` | Responsividade mobile | Implementado |
| `e2e/package.json` | Dependências Playwright | Implementado |

### `aes/` — Artefatos do Sistema AES

| Diretório | Conteúdo |
|-----------|----------|
| `aes/kanban.md` | Quadro de tickets (T001-T059) |
| `aes/plan/` | Specs detalhadas (T001-T059) |
| `aes/tickets/` | Tickets individuais com ACs e análise de riscos |
| `aes/shadow/` | Shadow docs (SD-PLAN, SD-BUILD, SD-VERIFY, SD-REVIEW, SD-LEARN) |
| `aes/metrics/` | Logs de verificação por ticket |

### `docs/` — Documentação Técnica

| Arquivo | Conteúdo |
|---------|----------|
| `docs/architecture.md` | Arquitetura de software |
| `docs/constraints.md` | Catálogo de restrições duras e moles |
| `docs/QUALITY_GATES.md` | Quality gates do projeto |
| `docs/literature_review.md` | Revisão da literatura |
| `docs/audit/baseline.md` | Este documento |
| `docs/audit/constraint-matrix.md` | Matriz de rastreabilidade de restrições |
| `docs/audit/findings.md` | Findings de auditoria |
| `docs/audit/architecture-decisions.md` | Decisões arquiteturais |
| `docs/audit/benchmark-plan.md` | Plano de benchmarks |
| `docs/school-timetable-auditoria-plano-refactoring.docx` | Relatório de auditoria externo (DOCX) |

### `data/` — Dados de Exemplo

| Arquivo | Conteúdo |
|---------|----------|
| `data/sample_school.json` | Escola pequena |
| `data/real_school.json` | Escola média (10 turmas, 15 professores, 12 disciplinas, 8 salas) |

## 4. Falhas Preexistentes Identificadas (Fase 0)

Estas falhas foram identificadas durante a Fase 0 e devem ser tratadas nas fases subsequentes:

| ID | Descrição | Severidade | Local |
|----|-----------|------------|-------|
| F-101 | CP-SAT: variáveis sobrescritas no dicionário (chave sem lesson_session_id) | BLOCKER | `src/timetable/cp_sat_baseline.py` |
| F-102 | CP-SAT: qualquer professor leciona qualquer disciplina (sem qualificações) | BLOCKER | `src/timetable/cp_sat_baseline.py` |
| F-103 | CP-SAT não implementa S03, S04, S06, S07 | MAJOR | `src/timetable/cp_sat_baseline.py` |
| F-008 | S02: limite baseado em número da hora (>= 13) sem relógio real | P1 | `src/timetable/constraints.py` |
| F-009 | S05: detecta A-B-A em vez de A-B-C-A | P1 | `src/timetable/constraints.py` |
| F-010 | S08: conta dias totais em vez de sequências consecutivas | P1 | `src/timetable/constraints.py` |
| F-011 | S09: compara contagens absolutas entre docentes | P1 | `src/timetable/constraints.py` |
| F-012 | S10: Python e CP-SAT usam condições diferentes | MAJOR | `src/timetable/constraints.py`, `cp_sat_baseline.py` |
| F-013 | H05: lista de disponibilidade vazia significa disponibilidade total | P0 | `src/timetable/models.py`, `constraints.py` |
| F-014 | H07/H08: relações familiares genéricas, risco de privacidade/discriminação | P0 | `src/timetable/constraints.py`, `cp_sat_baseline.py` |
| F-015 | Modelo de domínio simplificado (sem TimeSlot, AcademicPeriod, LessonSession, etc.) | P1 | `src/timetable/models.py` |
| F-016 | Solver executado no event loop HTTP (não assíncrono) | P0 | `src/timetable/cp_sat_baseline.py`, `backend/app/main.py` |
| F-017 | create_all usado em produção (sem Alembic) | P1 | `backend/app/main.py` |
| F-018 | Credenciais de desenvolvimento permitidas em arranque de produção | P0 | `docker/.env.example`, `backend/app/main.py` |
| F-019 | Sem isolamento de tenant (multi-tenancy) | P2 | `backend/app/models/` |
| F-020 | Sem auditoria de alterações a horários | P3 | `backend/app/models/schedule.py` |
| F-104 | seed.py usa dados hard-coded ("Turma A", "Prof. X", etc.) | MAJOR | `src/timetable/seed.py` |
| F-105 | seed.py é documentado como esqueleto, não construtor real | MAJOR | `src/timetable/seed.py` |
| F-106 | seed.py usa frozenset com tentativa de .add() | MAJOR | `src/timetable/seed.py` |
| F-107 | SA e Tabu Search iniciam com Horario() vazio | MAJOR | `src/timetable/local_search.py`, `backend/app/api/routers/schedules.py` |
| F-108 | CP-SAT ignora horário_inicial (não usa como seed/partial) | MAJOR | `src/timetable/cp_sat_baseline.py` |
| F-109 | Subgrupo_id não preservado nos movimentos locais | MAJOR | `src/timetable/local_search.py` |
| F-110 | Cache de avaliação não inclui identidade/versão do contexto | MAJOR | `src/timetable/objective.py` |
| F-111 | Serviço não aplica additional_unavailabilities | MAJOR | `backend/app/services/solver_service.py` |
| F-112 | Serviço não aplica qualificações docentes | MAJOR | `backend/app/services/solver_service.py` |
| F-113 | Serviço não aplica relações curriculares | MAJOR | `backend/app/services/solver_service.py` |
| F-114 | ScheduleVersion/ScheduleAssignment não persistidos | MAJOR | `backend/app/services/solver_service.py` |
| F-115 | Jobs mantidos apenas em memória (_solver_tasks dict) | MAJOR | `backend/app/services/solver_service.py` |
| F-116 | Consultas não filtradas por institution_id | P2 | `backend/app/api/routers/` |
| F-017 | create_all usado em produção | P1 | `backend/app/main.py` |

## 5. Limitações da Fase 0

- Os testes E2E Playwright não foram executados (requerem servidor frontend/backend ativo)
- Os testes de backend ainda não existem (nenhum ficheiro de teste em `backend/tests/`)
- Os testes frontend (Vitest) ainda não existem (nenhum ficheiro de teste em `web/src/`)
- O DOCX de auditoria foi lido, mas o link do ChatGPT não retornou conteúdo (requer autenticação)

## 6. Próximos Passos (Fase 1 - T048)

A Fase 1 (T048) deve:
1. Corrigir importações de Role para o módulo onde está realmente definido (models/user.py, não models/school.py)
2. Garantir que todos os routers que anotam User importam correctamente User
3. Importar select em app/core/deps.py ou reorganizar a função para não depender de símbolo ausente
4. Remover o ciclo main.py ↔ schedules.py movendo o limiter para módulo independente (app/core/limiter.py)
5. Rever todos os imports de arranque

---

**Status da Fase 0:** ✅ CONCLUÍDA — Nenhum código foi alterado nesta fase. Apenas leitura, execução de testes e documentação.
