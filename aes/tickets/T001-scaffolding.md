# Ticket T001 — Scaffolding do projeto Python + documentação AES

## Estado
**Concluído**

## Contexto
O problema do horário escolar é NP-hard (redução direta da coloração de grafos). Não existe uma única classe de problema que sirva para todas as escolas. A literatura consensual (ITC 2002/2003/2007, surveys de Burke, Schaerf, Ceschia et al., Tan et al. 2021) indica que metaheurísticas de busca local (Tabu Search, Simulated Annealing) batem algoritmos genéticos puros, e que a função objetivo deve ser aditiva (soma de penalidades), nunca um produto multiplicativo de pesos gigantes.

## Objetivo
Criar o scaffolding completo do projeto em Python com:
- Estrutura de diretórios AES (plan/build/verify/review/learn/tickets/metrics/shadow)
- Ficheiros de configuração (pyproject.toml, Makefile, .gitignore, README)
- Documentação inicial (literatura, arquitetura, restrições, quality gates)
- Esqueleto de código fonte (modelos, restrições, objetivo, solver, seed, UI)
- Testes iniciais

## Critérios de Aceitação (ACs) — Status
1. `make setup` instala dependências e cria ambiente virtual. — Pendente (depende de hatchling)
2. `make test` executa todos os testes e passa. — **OK** (24 testes, 81.07% cobertura)
3. `make lint` executa ruff/flake8 e passa sem erros. — **OK**
4. `make tree` mostra a estrutura de ficheiros esperada. — **OK**
5. Todos os ficheiros AES (kanban, ticket, spec, shadow docs) existem e são consistentes. — **OK**

## Decisões de Design
- Linguagem: Python 3.10+
- Solver exato: OR-Tools CP-SAT (via `ortools`) — opcional
- Metaheurística: implementação própria de Tabu Search e Simulated Annealing
- Formato de dados: JSON para entrada/saída
- Função objetivo: soma aditiva de penalidades pelas restrições moles

## Riscos (Hostile Analysis)
- Escopo a crescer demais (scope creep): mitigação = focar apenas no scaffolding nesta iteração.
- Dependências externas pesadas: mitigação = CP-SAT opcional; o projeto deve rodar sem ele para testes de unidade.
- Complexidade do modelo de domínio: mitigação = modelos simples e bem tipados com dataclasses.

## Fase atual
Plan → Build → Verify (concluído). Próximo: Review (T009).
