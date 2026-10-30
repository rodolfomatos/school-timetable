# Shadow Doc SD-BUILD-001 — Implementação do Scaffolding (T001)

## Proveniência
Build phase do ticket T001, concluída em 2026-10-29.

## O que foi construído
- Estrutura AES completa: `aes/{plan,build,verify,review,learn,tickets,metrics,shadow}`
- Código fonte em `src/timetable/`: `models.py`, `constraints.py`, `objective.py`, `seed.py`, `solver.py`, `cp_sat_baseline.py`, `local_search.py`, `ui.py`
- Testes em `tests/`: `test_models.py`, `test_constraints.py`, `test_objective.py`, `test_seed.py`, `test_integration.py` (24 testes)
- Dados de exemplo: `data/sample_school.json`
- Configuração: `pyproject.toml`, `Makefile`, `README.md`, `.gitignore`
- Documentação: `docs/architecture.md`, `docs/constraints.md`, `docs/QUALITY_GATES.md`

## Decisões tomadas durante o build
1. `ContextoRestricoes` definido em `constraints.py` (não em `models.py`) — corrigido após erro de importação.
2. Função objetivo aditiva (soma de penalidades), nunca produto multiplicativo — decisão arquitetural baseada na literatura.
3. `simulated_annealing` e `tabu_search` implementados em `local_search.py` como esqueleto; CP-SAT como wrapper opcional.

## Escore epistémico
Alta confiança na estrutura geral. Média confiança na implementação das metaheurísticas (não testada com dados reais de escola ainda).

## Próximos passos
- T004: Implementar CP-SAT completo (OR-Tools)
- T005: Aperfeiçoar Tabu Search / Simulated Annealing com movimentos de troca (exchange)
- T009: Revisão hostil
