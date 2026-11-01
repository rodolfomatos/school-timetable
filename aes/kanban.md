# AES Kanban — school-timetable (Web Platform Phase + Auditoria)

## Tickets

| ID | Título | Estado | Fase | Prioridade |
|----|--------|--------|------|------------|
| T001 | Scaffolding do projeto Python + documentação AES | Concluído | Plan/Build | Alta |
| T002 | Modelo de dados (entidades: turma, professor, disciplina, sala, slot) | Concluído | Plan/Build | Alta |
| T003 | Restrições duras e moles + função objetivo aditiva | Concluído | Plan/Build | Alta |
| T004 | Linha de base exata (CP-SAT / OR-Tools) | Concluído | Build | Alta |
| T005 | Metaheurística principal (Tabu Search / Simulated Annealing) | Concluído | Build | Alta |
| T006 | Seed parcial imutável (30% dos slots) | Concluído | Plan/Build | Média |
| T007 | Interface de ajuste manual ("insets de plástico") | Concluído | Build | Média |
| T008 | Testes unitários + integração + cobertura ≥ 80% | Concluído | Verify | Alta |
| T009 | Revisão hostil (peer review) | Concluído | Review | Alta |
| T010 | Captura de aprendizados (shadow docs) | Concluído | Learn | Média |
| T011 | Restrições de equilíbrio humano (S08-S10) + satisficing | Concluído | Plan/Build | Alta |
| T012 | Fix F-001: Tabu Search chave tabu sempre None | Concluído | Build | Alta (BLOCKER) |
| T013 | Fix F-002: Tabu Search tabu_set não sincronizado | Concluído | Build | Alta (MAJOR) |
| T014 | Fix F-003: Restrições moles S04-S07 não implementadas | Concluído | Build | Alta (MAJOR) |
| T015 | Fix F-004/F-005: CP-SAT S09/S10 penalização sem condição | Concluído | Build | Alta (MAJOR) |
| T016 | Fix F-006: Avaliação não incremental | Concluído | Build | Alta (MAJOR) |
| T017 | Fix F-007 a F-011: Findings MINOR | Concluído | Build | Média (MINOR) |
| T018 | Validação com dados reais de escola | Concluído | Build | Alta |
| T019 | Interface de linha de comando (CLI) | Concluído | Build | Alta |
| T020 | Exportação iCal/CSV | Concluído | Build | Média |
| T021 | Property-based testing para restrições duras | Concluído | Build | Média |
| T022 | Backend API FastAPI + autenticação JWT + RBAC | Concluído | Build | Alta |
| T023 | Modelo de dados alargado (salas específicas, setup/limpeza, almoço, furos, não-periodicidade) | Concluído | Build | Alta |
| T024 | Frontend React + ilabuporto-design-system (calendário, tabelas, formulários) | Concluído | Build | Alta |
| T025 | Fluxo de contestações docente ↔ admin | Concluído | Build | Alta |
| T026 | Docker Compose (on-premise / SaaS) | Concluído | Build | Alta |
| T027 | Testes E2E com Playwright (fluxos completos) | Concluído | Verify | Alta |
| T028 | Revisão hostil de segurança e UX | Concluído | Review | Alta |
| T029 | Captura de aprendizados da fase web | Concluído | Learn | Média |
| T030 | Fix F-012 (BLOCKER): JWT em cookies httpOnly | Concluído | Build | Alta (BLOCKER) |
| T031 | Fix F-013 (MAJOR): Sanitização de entrada XSS | Concluído | Build | Alta (MAJOR) |
| T032 | Fix F-014 (MAJOR): Rate limiting no solver | Concluído | Build | Alta (MAJOR) |
| T033 | Fix F-015 (MAJOR): Credenciais no .env.example | Concluído | Build | Alta (MAJOR) |
| T034 | Fix F-016 (MINOR): Contraste WCAG AA | Concluído | Build | Média (MINOR) |
| T035 | Fix F-017 (MINOR): Loading states consistentes | Concluído | Build | Média (MINOR) |
| T036 | Fase 0: Baseline e Inventário (Auditoria) | Concluído | Build | Alta |
| T037 | Fase 1: Auditoria de Restrições (Auditoria) | Concluído | Build | Alta |
| T038 | Fase 2: Integridade do Modelo CP-SAT (Auditoria) | Concluído | Build | Alta |
| T039 | Fase 3: Seed e Validador Independente (Auditoria) | Concluído | Build | Alta |
| T040 | Fase 4: Resultado e Ciclo de Vida do Solver (Auditoria) | Concluído | Build | Alta |
| T041 | Fase 5: Objetivo e Metaheurísticas (Auditoria) | Concluído | Build | Alta |
| T042 | Fase 6: Avaliação Incremental e Cache (Auditoria) | Em Progresso | Build | Alta |
| T043 | Fase 7: Backend e Operação (Auditoria) | Em Progresso | Build | Alta |
| T044 | Fase 8: Testes e Benchmarks (Auditoria) | Concluído | Verify | Alta |
| T045 | Fase 9: Entregáveis (Auditoria) | Concluído | Learn | Alta |
| T046 | Suporte a subgrupos de turma (divisão de aulas) | Em Progresso | Build | Alta |
| T047 | Fase 0: Baseline e verificação independente (Auditoria) | Concluído | Review | P0 |
| T048 | Fase 1: Bootstrap e imports do backend (Auditoria) | Concluído | Build | P0 |
| T049 | Fase 2: Integridade do modelo SQLAlchemy (Auditoria) | Concluído | Build | P0 |
| T050 | Fase 3: Autenticação e privilégios (Auditoria) | Concluído | Build | P0 |
| T051 | Fase 3: Modelo de domínio e integração (Auditoria) | Concluído | Build | P0 |
| T052 | Fase 3: Construção de solução inicial (Auditoria) | Concluído | Build | P0 |
| T053 | Fase 4: Correção matemática do CP-SAT (Auditoria) | Concluído | Build | P0 |
| T054 | Fase 4: Semântica dos subgrupos (Auditoria) | Concluído | Build | P0 |
| T055 | Fase 5: Consistência das restrições S01–S10 (Auditoria) | Concluído | Build | P1 |
| T056 | Fase 6: Cache e avaliação incremental (Auditoria) | Concluído | Build | P1 |
| T057 | Fase 7: SolverResult e jobs persistentes (Auditoria) | Pendente | Build | P1 |
| T058 | Fase 7: Multi-tenancy, migrações e produção (Auditoria) | Pendente | Build | P1 |
| T059 | Fase 8: Verificação epistemológica do AES (Auditoria) | Pendente | Learn | P1 |

## Regras
- Um ticket só entra em "Build" com spec aprovada em "Plan".
- Não há código sem ticket associado.
- Qualquer regressão abre ticket novo.
- Todos os testes E2E com Playwright devem passar antes de fechar o ticket.
