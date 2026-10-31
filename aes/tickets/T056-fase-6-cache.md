# Ticket T056 — Fase 6: Cache e avaliação incremental

## Contexto
Cache global não inclui identidade/versão do contexto; não existe avaliação incremental verdadeira.

## Objetivo
Corrigir a contaminação do cache entre contextos e clarificar a diferença entre cache integral e avaliação incremental.

## Critérios de Aceitação
[ ] Mesmo horário em contextos diferentes nunca partilha avaliação indevidamente.
[ ] Alterar pesos/regras invalida ou muda a chave do cache.
[ ] Subgrupos e IDs de sessão participam na identidade canónica.
[ ] Testes aleatórios comparam cache com avaliação integral.
[ ] Se avaliação incremental for implementada, delta score coincide com avaliação integral após sequências de movimentos.
[ ] Memória do cache é limitada e observável.

## Fase atual
Plan → Build → Verify.
