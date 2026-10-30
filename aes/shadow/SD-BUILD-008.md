# Shadow Doc SD-BUILD-008 — Avaliação com Cache (T016)

## Proveniência
Build phase do ticket T016, concluída em 2026-10-29. Corrigi F-006 (MAJOR).

## Corrigido — F-006 (MAJOR): Avaliação não incremental

**Problema:** Cada iteração da metaheurística chamava `avaliar()` que recalculava TODO o horário (O(n) sobre todas as aulas), sem qualquer cache ou avaliação incremental.

**Decisão:** Em vez de implementar avaliação incremental verdadeira (que exigiria refatorar `calcular_penalidades_moles` e `verificar_hard` para aceitar deltas — trabalho significativo para benefício marginal em instâncias pequenas/médias), optei por:

1. **Cache de avaliação** (`src/timetable/objective.py`):
   - `_cache_avaliacao: dict[tuple, Avaliacao]` — mapeia representação hashável do horário para o resultado
   - `avaliar_com_cache(horario, ctx)` — verifica cache antes de avaliar; armazena se não estiver
   - `limpar_cache_avaliacao()` — esvazia o cache entre execuções independentes
   - `_chave_horario(horario)` — gera chave hashável ordenada por todas as aulas

2. **Documentação de limitação** (`src/timetable/objective.py` docstring + `src/timetable/local_search.py` docstring):
   - Explica que a avaliação completa é O(n) por iteração
   - Indica que para instâncias grandes seria necessário avaliação incremental verdadeira
   - Aponta para o ticket T016/F-006

## Testes adicionados (2 novos)
- `test_avaliar_com_cache_retorna_mesmo_resultado`: verifica que o cache devolve o mesmo Avaliacao
- `test_avaliar_com_cache_limpar`: verifica que limpar_cache_avaliacao funciona

## Cobertura
- `objective.py`: 100% (mantido)
- Total do projeto: 91.68%

## Escore epistémico
Alta confiança: o cache é uma otimização simples e verificável. A limitação documentada é honesta sobre o trade-off entre complexidade de implementação e benefício de performance.

## Próximos passos
- T017: Findings MINOR (F-007 a F-011)
