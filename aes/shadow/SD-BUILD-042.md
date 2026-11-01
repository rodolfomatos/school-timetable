# Shadow Doc SD-BUILD-042 — T055 Fase 5: Consistência das restrições S01–S10

## Proveniência
Fase 5 do plano de auditoria AES T047–T059, concluída em 01/11/2026 sobre o
commit `26ef5f1` (T054 incluído).

## Objetivo
Auditoria final de consistência: especificação formal, testes de fronteira e
confirmação de alinhamento CP-SAT vs Python para S01–S10.

## Decisões tomadas
- Especificação formal em `docs/spec/soft_constraints_spec.md`: cada regra
  com fórmula, pesos, limites, implementação Python/CP-SAT e requisitos de
  teste.
- Testes de fronteira em `tests/test_t055_soft_constraints.py`: 36 testes
  (base, fronteira, contra-exemplo) cobrindo S01–S10.
- Alinhamentos S02/S05/S08/S09/S10 já feitos em T053; T055 documenta e
  testa a consistência.
- Nenhuma regra soft transformada em hard; reificações bidireccionais onde
  necessário (S05, S08, S10).

## Evidência
- `docs/spec/soft_constraints_spec.md`: 10 regras × fórmula + pesos + limites.
- `tests/test_t055_soft_constraints.py`: 36 testes (4 por regra em média).
- Suite completa: 89.71% cobertura.
- Backend: 9 passed, import OK, lint OK.

## Escore epistémico
Alta confiança — cada regra mole tem especificação, implementação paralela
em Python e CP-SAT com semântica idêntica, testada independentemente com
casos de fronteira.

## Próximos passos
- T056: cache e avaliação incremental.
- T057: SolverResult e jobs persistentes.
- T058: multi-tenancy, migrações, produção.
- T059: verificação epistemológica final.