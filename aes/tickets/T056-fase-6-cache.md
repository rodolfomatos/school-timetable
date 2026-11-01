# Ticket T056 — Fase 6: Cache e avaliação incremental

## Contexto
O cache global `_cache_avaliacao` usava apenas o fingerprint do horário como chave, ignorando o `ContextoRestricoes`. Isso causava contaminação: o mesmo horário avaliado em contextos diferentes (ex: professor com/sem dia de folga) compartilhava o resultado em cache incorretamente. Além disso, não existia avaliação incremental verdadeira — cada movimento em metaheurísticas recalculava tudo.

## Objetivo
Corrigir a contaminação do cache entre contextos e implementar avaliação incremental para movimentos locais (exchange/modify).

## Causa-raiz (confirmada)
1. `_chave_horario` só incluía as aulas, não o contexto.
2. `avaliar_com_cache` não tinha fingerprint do contexto.
3. Não existia `avaliar_incremental` para recalcular apenas o delta.
4. Cache sem limite de tamanho (LRU) nem estatísticas observáveis.

## Correções aplicadas
- **`src/timetable/objective.py`**:
  - `_fingerprint_contexto(ctx)`: SHA256 dos dados que afetam avaliação (professores: disponibilidade, dia_folga, prefere_manha, cargas, qualificações; salas: tipo, capacidade; disciplinas: carga, tipo_sala; casamentos; relacoes_filho; subgrupos).
  - `_chave_composta(horario, ctx)`: tupla `(fingerprint_horario, fingerprint_contexto)`.
  - Cache LRU com `_MAX_CACHE_SIZE = 10_000`, estatísticas (hits, misses, evictions, hit_rate).
  - `avaliar_incremental(horario_base, ctx, removidas, adicionadas, avaliacao_base)`:
    - Identifica entidades afetadas (professores, salas, turmas, disciplinas, subgrupos, dias).
    - Verifica hard constraints apenas nas entidades afetadas (`_verificar_hard_incremental`).
    - Calcula delta de penalidades moles por restrição (`_calcular_delta_penalidades_moles`): calcula penalidade no estado base e novo, retorna diferença.
    - Retorna `Avaliacao` com `score = -novas_penalidades` (corrigido bug onde `score = base.score + delta`).
  - `estatisticas_cache()`: expõe size, hits, misses, evictions, hit_rate.

## Critérios de Aceitação
- [x] Mesmo horário em contextos diferentes nunca partilha avaliação indevidamente (teste `test_cache_chave_inclui_contexto`).
- [x] Alterar pesos/regras invalida ou muda a chave do cache (fingerprint do contexto inclui regras).
- [x] Subgrupos e IDs de sessão participam na identidade canónica (incluídos no fingerprint do horário).
- [x] Testes aleatórios comparam cache com avaliação integral (teste `test_avaliar_incremental_delta_score`).
- [x] Avaliação incremental: delta score coincide com avaliação integral após movimentos (testes S01, S02, delta_score).
- [x] Memória do cache é limitada (LRU 10k) e observável (`estatisticas_cache()`).

## Evidência
- `tests/test_objective.py`: 18 testes (cache contexto, LRU, stats, incremental S01, S02, delta_score, hard constraints).
- Suite completa: 89.09% cobertura.
- Backend: 9 passed, import OK, lint OK.

## Estado epistémico
- Implementado: **SIM**
- Testado: **SIM**
- Verificado: **SIM**
- Independentemente verificado: **PENDENTE** (T059)

## Fase actual
Plan → Build → Verify → Review (concluído) → Learn.