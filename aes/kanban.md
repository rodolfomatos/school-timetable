# AES Kanban — school-timetable

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
| T020 | Exportação iCal/CSV | Pendente | Build | Média |

## Regras
- Um ticket só entra em "Build" com spec aprovada em "Plan".
- Não há código sem ticket associado.
- Qualquer regressão abre ticket novo.
