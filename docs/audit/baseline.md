# Baseline de Auditoria — school-timetable

**Data:** 31 de outubro de 2026  
**Versão:** 1.0  
**Repositório:** https://github.com/rodolfomatos/school-timetable  
**Commit HEAD:** 6eb6976 (fix(T030-T035): corrigir findings da revisão hostil)  
**Fase:** Fase 0 — Baseline e Inventário (apenas leitura, nenhuma alteração de código)

---

## 1. Ambiente de Execução

| Item | Versão |
|------|--------|
| Python | 3.10.12 |
| Node.js | v24.18.0 |
| npm | 11.16.0 |
| OR-Tools | 9.15.6755 |
| FastAPI | 0.138.0 |
| SQLAlchemy | 2.0.51 |
| Hypothesis | 6.168.5 |
| pytest | 9.1.1 |
| ruff | 0.15.20 |
| mypy | 2.1.0 |
| Playwright | 1.40.0 (e2e/) |
| Vitest | 1.6.1 (web/) |

---

## 2. Comandos de Teste

| Comando | Propósito | Status |
|---------|-----------|--------|
| `PYTHONPATH=src python3 -m pytest tests/ --cov=src/timetable` | Testes Python do solver | ✅ Passa (92.12% cobertura) |
| `ruff check src tests` | Lint Python | ❌ 8 erros (todos fixable com --fix) |
| `ruff format --check src tests` | Formatação Python | ✅ Limpo |
| `cd backend && python3 -m pytest tests/` | Testes backend FastAPI | ⚠️ Nenhum teste encontrado |
| `cd web && npm test` | Testes frontend Vitest | ⚠️ Nenhum arquivo de teste encontrado |
| `cd e2e && npx playwright test` | Testes E2E Playwright | ⚠️ Não executado (requer servidor ativo) |

---

## 3. Estrutura do Repositório

### `src/timetable/` — Núcleo do Solver Python

| Módulo | Responsabilidade | Linhas | Cobertura | Status |
|--------|-----------------|--------|-----------|--------|
| `models.py` | Slot, Sala, Professor, Turma, Disciplina, Aula, Horario, RelacaoCasamento, RelacaoFilho | 86 | 95% | Implementado |
| `constraints.py` | Restrições duras H01-H08 e moles S01-S10 (adiitivas) | 154 | 94% | Implementado |
| `objective.py` | Função objetivo aditiva: score = -Σ(penalidade × peso) | 32 | 100% | Implementado |
| `seed.py` | Geração de seed parcial imutável (~30% dos slots) | 20 | 100% | Esqueleto |
| `solver.py` | Interface abstrata SolverBase | 8 | 0% | Esqueleto |
| `cp_sat_baseline.py` | Wrapper OR-Tools CP-SAT (opcional) | 139 | 89% | Esqueleto (fallback) |
| `local_search.py` | Tabu Search e Simulated Annealing | 134 | 91% | Implementado |
| `ui.py` | Exportação/importação JSON (insets de plástico) | 85 | 88% | Esqueleto |
| `export.py` | Exportação CSV e iCal (.ics) | 52 | 100% | Implementado |

**Total statements: 711 | Missing: 56 | Cobertura: 92.12%**

### `backend/` — API FastAPI

| Módulo | Responsabilidade | Status |
|--------|-----------------|--------|
| `app/main.py` | Aplicação FastAPI, routers, CORS, startup init_db | Implementado |
| `app/core/config.py` | Configurações via Pydantic Settings | Implementado |
| `app/core/security.py` | Hash bcrypt, JWT criação/verificação, decode | Implementado |
| `app/core/deps.py` | get_db, get_current_user (cookie httpOnly), require_role | Implementado |
| `app/db/session.py` | SQLAlchemy async engine + session | Implementado |
| `app/db/base.py` | Base declarativa | Implementado |
| `app/models/user.py` | User, Role (admin/teacher/student/coordinator) | Implementado |
| `app/models/school.py` | Course, Room, Subject, Class, Teacher (alargado) | Implementado |
| `app/models/schedule.py` | ScheduleVersion, ScheduleAssignment, Unavailability, Dispute | Implementado |
| `app/schemas/user.py` | Schemas Pydantic para utilizadores | Implementado |
| `app/schemas/school.py` | Schemas Pydantic para entidades da escola | Implementado |
| `app/schemas/schedule.py` | Schemas Pydantic para horários, disputas | Implementado |
| `app/api/routers/auth.py` | /auth/register, /auth/login, /auth/refresh, /auth/logout | Implementado (cookies httpOnly) |
| `app/api/routers/users.py` | CRUD utilizadores | Implementado |
| `app/api/routers/rooms.py` | CRUD salas | Implementado |
| `app/api/routers/subjects.py` | CRUD disciplinas | Implementado |
| `app/api/routers/classes.py` | CRUD turmas | Implementado |
| `app/api/routers/courses.py` | CRUD cursos | Implementado |
| `app/api/routers/schedules.py` | /scheduler/run, /scheduler/status/{task_id}, /schedule/versions | Implementado (rate limited 5/min) |
| `app/api/routers/disputes.py` | /disputes (criar, listar, aceitar/rejeitar) | Implementado |
| `app/services/solver_service.py` | Wrapper sobre solver Python (execução em ThreadPool) | Implementado |
| `backend/requirements.txt` | Dependências Python | Implementado |

### `web/` — Frontend React

| Módulo | Responsabilidade | Status |
|--------|-----------------|--------|
| `web/src/App.tsx` | Roteador com proteção de rotas (RequireAuth, RequireRole) | Implementado |
| `web/src/components/Navbar.tsx` | Navbar institucional com Brand | Implementado |
| `web/src/components/Sidebar.tsx` | Sidebar com itens condicionais por papel | Implementado |
| `web/src/pages/Login.tsx` | Página de login (cookie httpOnly) | Implementado |
| `web/src/pages/Dashboard.tsx` | Dashboard com estatísticas e botão gerar horário | Implementado |
| `web/src/pages/TeacherCalendar.tsx` | Calendário de indisponibilidades com justificativas | Implementado |
| `web/src/pages/ScheduleTable.tsx` | Tabela de horário por turma/docente/sala | Implementado |
| `web/src/pages/Disputes.tsx` | Portal de contestações (submeter, aceitar/rejeitar) | Implementado |
| `web/src/pages/ManageEntities.tsx` | Gestão genérica de utilizadores, salas, disciplinas, turmas | Implementado |
| `web/src/services/api.ts` | Axios com interceptores de auth, withCredentials | Implementado |
| `web/src/stores/authStore.ts` | Zustand (sem persist, token em memória) | Implementado |
| `web/src/stores/scheduleStore.ts` | Estado do horário + helpers de consulta | Implementado |
| `web/src/types/index.ts` | Tipos TypeScript para todas as entidades | Implementado |
| `web/src/utils/sanitize.ts` | Sanitização HTML com DOMPurify (anti-XSS) | Implementado |
| `web/src/index.css` | Tailwind + estilos do design system + utilitários de contraste | Implementado |
| `web/package.json` | Dependências Node | Implementado |

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
| `e2e/playwright.config.ts` | Configuração Playwright (Chromium, Firefox, WebKit, mobile) | Implementado |
| `e2e/tests/teacher-calendar.spec.ts` | Docente marca indisponibilidade | Implementado |
| `e2e/tests/admin-generate.spec.ts` | Admin gera horário | Implementado |
| `e2e/tests/disputes.spec.ts` | Docente contesta slot | Implementado |
| `e2e/tests/accessibility.spec.ts` | Navegação por teclado, contraste | Implementado |
| `e2e/tests/mobile.spec.ts` | Responsividade mobile | Implementado |
| `e2e/package.json` | Dependências Playwright | Implementado |

### `aes/` — Artefatos do Sistema AES

| Diretório | Conteúdo |
|-----------|----------|
| `aes/kanban.md` | Quadro de tickets (T001-T045) |
| `aes/plan/` | Specs detalhadas (T001-T045) |
| `aes/tickets/` | Tickets individuais com ACs e análise de riscos |
| `aes/shadow/` | Shadow docs (SD-PLAN, SD-BUILD, SD-VERIFY, SD-REVIEW, SD-LEARN) |
| `aes/metrics/` | Logs de verificação por ticket |

### `docs/` — Documentação Técnica

| Arquivo | Conteúdo |
|---------|----------|
| `docs/architecture.md` | Arquitetura de software |
| `docs/constraints.md` | Catálogo de restrições duras e moles |
| `docs/QUALITY_GATES.md` | Quality gates do projeto |
| `docs/literature_review.md` | Revisão da literatura (ITC 2007, etc.) |
| `docs/school-timetable-auditoria-plano-refactoring.docx` | Relatório de auditoria externo (DOCX) |

### `data/` — Dados de Exemplo

| Arquivo | Conteúdo |
|---------|----------|
| `data/sample_school.json` | Escola pequena (2 turmas, 2 professores, 2 disciplinas) |
| `data/real_school.json` | Escola média (10 turmas, 15 professores, 12 disciplinas, 8 salas) |

---

## 4. Falhas Preexistentes Identificadas (Fase 0)

Estas falhas foram identificadas durante a Fase 0 e devem ser tratadas nas fases subsequentes:

| ID | Descrição | Severidade | Local |
|----|-----------|------------|-------|
| F-001 (antigo) | Tabu Search: chave tabu sempre None | BLOCKER | `src/timetable/local_search.py` — Corrigido em T012 |
| F-002 (antigo) | tabu_set não sincronizado com deque | MAJOR | `src/timetable/local_search.py` — Corrigido em T013 |
| F-003 (antigo) | Restrições moles S04-S07 não implementadas | MAJOR | `src/timetable/constraints.py` — Corrigido em T014 |
| F-004 (antigo) | CP-SAT S09 penaliza sem condição > 2 | MAJOR | `src/timetable/cp_sat_baseline.py` — Corrigido em T015 |
| F-005 (antigo) | CP-SAT S10 penaliza sem condição ≥ 5 | MAJOR | `src/timetable/cp_sat_baseline.py` — Corrigido em T015 |
| F-006 (antigo) | Avaliação não incremental | MAJOR | `src/timetable/objective.py` — Parcialmente corrigido em T016 (cache adicionado) |
| F-007 (antigo) | S03 lógica ofuscada | MINOR | `src/timetable/constraints.py` — Corrigido em T017 |
| F-008 (antigo) | UI sem verificação de conflitos | MINOR | `src/timetable/ui.py` — Corrigido em T017 (parâmetro validar) |
| F-009 (antigo) | JSON sem validação de estrutura | MINOR | `src/timetable/ui.py` — Corrigido em T017 (_validar_estrutura_json) |
| F-010 (antigo) | Testes de integração fracos | MINOR | `tests/test_integration.py` — Corrigido em T017 (verificar_hard == []) |
| F-011 (antigo) | Parâmetro não usado | MINOR | `src/timetable/local_search.py` — Corrigido em T017 (_slots_disponiveis) |
| F-012 | JWT armazenado em localStorage | BLOCKER | `web/src/stores/authStore.ts` — Corrigido em T030 (removido persist) |
| F-013 | Sem sanitização de entrada XSS | MAJOR | `web/src/pages/Disputes.tsx` — Corrigido em T031 (dompurify) |
| F-014 | Sem rate limiting no solver | MAJOR | `backend/app/api/routers/schedules.py` — Corrigido em T032 (slowapi) |
| F-015 | Credenciais no .env.example | MAJOR | `docker/.env.example` — Corrigido em T033 (placeholders) |
| F-016 | Contraste WCAG AA | MINOR | `web/src/index.css` — Corrigido em T034 (classes de texto) |
| F-017 | Loading states inconsistentes | MINOR | `web/src/pages/Disputes.tsx` — Corrigido em T035 (loading states) |

### Novos Findings da Auditoria Externa (DOCX)

O documento de auditoria externa (docs/school-timetable-auditoria-plano-refactoring.docx) identifica os seguintes problemas críticos **não ainda abordados**:

| ID | Descrição | Severidade | Local |
|----|-----------|------------|-------|
| F-101 | CP-SAT: variáveis sobrescritas no dicionário (chave sem lesson_session_id) | BLOCKER | `src/timetable/cp_sat_baseline.py` |
| F-102 | CP-SAT: qualquer professor leciona qualquer disciplina (sem qualificações) | BLOCKER | `src/timetable/cp_sat_baseline.py` |
| F-103 | CP-SAT não equivalente ao validador Python | MAJOR | `src/timetable/cp_sat_baseline.py` + `src/timetable/constraints.py` |
| F-004 (revisitado) | Seed parcial não é solução viável (valores hard-coded) | MAJOR | `src/timetable/seed.py` |
| F-005 (revisitado) | Operadores de movimento limitados (apenas exchange/modify slot) | MAJOR | `src/timetable/local_search.py` |
| F-006 (revisitado) | Função objetivo aditiva insuficiente (não lexicográfica) | MAJOR | `src/timetable/objective.py` |
| F-007 (revisitado) | Cache global sem identificação de instância de problema | MAJOR | `src/timetable/objective.py` (_cache_avaliacao) |
| F-008 | S02: limite baseado em número da hora, sem relógio real | P1 | `src/timetable/constraints.py` |
| F-009 | S05: detecta A-B-A em vez de A-B-C-A | P1 | `src/timetable/constraints.py` |
| F-010 | S08: conta dias totais em vez de sequências | P1 | `src/timetable/constraints.py` |
| F-011 | S09: comparação de contagens absolutas entre docentes | P1 | `src/timetable/constraints.py` |
| F-012 | S10: divergência CP-SAT/validador | P1 | `src/timetable/cp_sat_baseline.py` + `src/timetable/constraints.py` |
| F-013 | H05: lista vazia significa disponibilidade total (tri-state necessário) | P0 | `src/timetable/models.py` |
| F-014 | H07/H08: relações familiares genéricas, risco de privacidade/discriminação | P0 | `src/timetable/models.py` |
| F-015 | Modelo de domínio simplificado (sem TimeSlot, AcademicPeriod, LessonSession, etc.) | P1 | `src/timetable/models.py` |
| F-016 | Solver executado no event loop HTTP (não assíncrono) | P0 | `backend/app/main.py` |
| F-017 | create_all usado em produção (sem Alembic) | P1 | `backend/app/main.py` |
| F-018 | Credenciais de desenvolvimento permitidas em arranque de produção | P0 | `docker/.env.example`, `backend/app/main.py` |
| F-019 | Sem isolamento de tenant (multi-tenancy) | P2 | `backend/app/models/` |
| F-020 | Sem auditoria de alterações a horários/aprovações | P3 | `backend/app/models/schedule.py` |

---

## 5. Limitações da Fase 0

- Os testes E2E Playwright não foram executados (requerem servidor frontend/backend ativo)
- Os testes de backend ainda não existem (nenhum arquivo de teste em `backend/tests/`)
- Os testes frontend (Vitest) ainda não existem (nenhum arquivo de teste em `web/src/`)
- O DOCX de auditoria foi lido, mas o link do ChatGPT não retornou conteúdo (requer autenticação)

---

## 6. Próximos Passos (Fase 1)

A Fase 1 (T037) deve:
1. Extrair todas as restrições hard e soft de docs/constraints.md e do código
2. Criar docs/audit/constraint-matrix.md com: ID, definição formal, âmbito, implementação Python, implementação CP-SAT, peso/penalização, testes, estado e discrepâncias
3. Confirmar especificamente H01-H08 e S01-S10
4. Verificar suspeitas sobre S02, S05, S08, S09, S10
5. Verificar se regras H07/H08 são justificadas, necessárias e proporcionais

---

**Status da Fase 0:** ✅ CONCLUÍDA — Nenhum código foi alterado nesta fase. Apenas leitura, execução de testes e documentação.
