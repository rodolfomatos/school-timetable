# Shadow Doc SD-BUILD-043 — T056 Fase 6: Cache e avaliação incremental

## Proveniência
Fase 6 do plano de auditoria AES T047–T059, concluída em 01/11/2026 sobre o
commit `27ceec7` (T055 incluído).

## Objetivo
Corrigir contaminação do cache entre contextos e implementar avaliação
incremental para movimentos locais (exchange/modify) em metaheurísticas.

## Decisões tomadas
- **Fingerprint do contexto**: SHA256 dos dados que afetam avaliação
  (professores: disponibilidade, dia_folga, prefere_manha, cargas, qualificações;
  salas: tipo, capacidade; disciplinas: carga, tipo_sala; casamentos; relacoes_filho;
  subgrupos). Chave composta = `(fingerprint_horario, fingerprint_contexto)`.
- **Cache LRU**: `_MAX_CACHE_SIZE = 10_000`, estatísticas expostas via
  `estatisticas_cache()` (hits, misses, evictions, hit_rate).
- **Avaliação incremental**: `avaliar_incremental(horario_base, ctx, removidas, adicionadas, avaliacao_base)`:
  - Identifica entidades afetadas.
  - Verifica hard constraints apenas nas afetadas.
  - Calcula delta de penalidades por restrição: `fn(estado_novo) - fn(estado_base)`.
  - Bug corrigido: `score = -novas_penalidades` (não `base.score + delta`).
- **Testes**: 18 testes em `test_objective.py` cobrindo cache contexto, LRU, stats,
  incremental S01, S02, delta_score, hard constraints.

## Evidência
- `tests/test_objective.py`: 18 testes passando.
- Suite completa: 89.09% cobertura.
- Backend: 9 passed, import OK, lint OK.

## Escore epistémico
Alta confiança — cache agora isola contextos corretamente, avaliação incremental
testada contra avaliação completa (delta_score), e LRU evita vazamento de memória.

## Próximos passos
- T057: SolverResult e jobs persistentes.
- T058: Multi-tenancy, migrações, produção.
- T059: Verificação epistemológica final.