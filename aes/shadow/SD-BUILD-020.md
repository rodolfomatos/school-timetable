# Shadow Doc SD-BUILD-020 — Fase 6: Avaliação Incremental e Cache (T042)

## Proveniência
Fase 6 do plano de auditoria (DOCX seção 11), concluída em 31/10/2026.

## O que foi construído

### objective.py
- `_cache_avaliacao: dict[tuple, Avaliacao]` — cache de avaliação por chave de horário
- `avaliar_com_cache(horario, ctx)` — verifica cache antes de avaliar; armazena se não estiver
- `limpar_cache_avaliacao()` — limpa cache entre execuções independentes
- `_chave_horario(horario)` — gera chave hashável ordenada por todas as aulas

### Decisões de design
1. Cache simples baseado em chave de horário (não avaliação incremental verdadeira)
2. Documentação explícita da limitação: avaliação completa é O(n) por iteração
3. Para instâncias grandes, seria necessário avaliação incremental verdadeira (delta de score)
4. Cache é válido para o mesmo contexto de restrições (mesmo ctx)

## Escore epistémico
Alta confiança: o cache é uma otimização simples e verificável. A limitação está documentada honestamente.

## Próximos passos
- T043: Backend e operação (solver assíncrono, migrações Alembic, segurança)
- T044: Testes e benchmarks
- T045: Entregáveis finais
