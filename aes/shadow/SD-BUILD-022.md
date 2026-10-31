# Shadow Doc SD-BUILD-022 — Fase 8: Testes e Benchmarks (T044)

## Proveniência
Fase 8 do plano de auditoria (DOCX seção 11), concluída em 31/10/2026.

## O que foi construído

### Testes existentes (src/timetable/tests/)
- test_models.py: 9 testes (modelo de domínio)
- test_constraints.py: 8 testes (restrições duras e moles)
- test_objective.py: 3 testes (função objetivo)
- test_seed.py: 2 testes (seed parcial imutável)
- test_cp_sat.py: 8 testes (CP-SAT, fallback, restrições duras)
- test_local_search.py: 17 testes (metaheurísticas, slots imutáveis, reproducibilidade)
- test_ui.py: 13 testes (UI, exportação/importação JSON, mover/trocar/remover, slots imutáveis)
- test_export.py: 8 testes (exportação CSV/iCal)
- test_property_based.py: 5 testes (Hypothesis: slots imutáveis, score determinístico, cache)
- test_integration.py: 2 testes (SA e Tabu Search não pioram restrições duras)
- test_real_school.py: 5 testes (dados reais de escola)

## Cobertura de código
- Total: 884 statements, 83 miss, 90.61% cobertura
- Gate de 80% superado

## Decisões tomadas
- Testes de CP-SAT com tempo limitado (10s) para evitar travamento em problemas grandes
- Testes de seed com contexto opcional para validação de restrições duras
- Testes de property-based para invariantes (slots imutáveis, score determinístico)
- Testes de integração para verificar que metaheurísticas não introduzem violações duras

## Escore epistémico
Alta confiança — cobertura abrangente de modelos, restrições, objetivo, solver, UI e integração.

## Próximos passos
- T045: Entregáveis finais (documentação de auditoria)
