# Shadow Doc SD-BUILD-041 — T054 Fase 4: Semântica dos subgrupos

## Proveniência
Fase 4 do plano de auditoria AES T047–T059, concluída em 01/11/2026 sobre o
commit `35d7afd` (T053 incluído).

## Objetivo
Completar o suporte a subgrupos: impedir sobreposição turma inteira ↔ subgrupo,
permitir subgrupos paralelos, preservar `subgrupo_id` em movimentos locais.

## Decisões tomadas
- **H03 Python**: `turma_ocupada_em` agora verifica turma inteira + subgrupo
  especificado (ou todos os subgrupos se `subgrupo_id=None`).
- **H03 CP-SAT**: Para turmas com subgrupos, adiciona restrição
  `soma(turma_inteira + subgrupo) ≤ 1` por slot, além da restrição por
  subgrupo individual.
- **Local Search**: `exchange` e `modify` preservam `subgrupo_id` ao
  construir novas `Aula`.
- **Domínio**: `EntradaCurricular.subgrupo_id` já existia; validador agora
  bloqueia conflitos correctamente.

## Evidência
- `tests/test_t054_subgrupos.py`: 5 testes (H03 bloqueia inteira↔subgrupo,
  subgrupos paralelos, operadores preservam ID, CP-SAT H03).
- Suite completa: 89.36% cobertura.
- Backend: 9 passed, import OK, lint OK.

## Escore epistémico
Alta confiança — H03 agora é simétrico e consistente entre Python e CP-SAT;
operadores locais não perdem informação de subgrupo.

## Próximos passos
- T055: consistência das restrições S01–S10 (auditoria final).
- T056: cache e avaliação incremental.
- T057: SolverResult e jobs persistentes.
- T058: multi-tenancy, migrações, produção.
- T059: verificação epistemológica final.