# AES Plan Spec — T056 Fase 6: Cache e avaliação incremental

## 1. Sumário Executivo
Corrigir a contaminação do cache entre contextos e clarificar a diferença entre cache integral e avaliação incremental.

## 2. Objetivo
- Incluir na chave do cache a identidade/versão do ProblemInstance e do ConstraintProfile.
- Incluir todos os elementos relevantes da solução, incluindo subgrupo e identidade da sessão.
- Preferir cache scoped à execução/instância em vez de dicionário global.
- Definir limite de memória e política de eviction.
- Renomear documentação: cache de resultados não é avaliação incremental.
- Só implementar avaliação incremental quando houver cálculo de deltas por restrição e validação contra cálculo integral.

## 3. Critérios de Aceitação
[ ] Mesmo horário em contextos diferentes nunca partilha avaliação indevidamente.
[ ] Alterar pesos/regras invalida ou muda a chave do cache.
[ ] Subgrupos e IDs de sessão participam na identidade canónica.
[ ] Testes aleatórios comparam cache com avaliação integral.
[ ] Se avaliação incremental for implementada, delta score coincide com avaliação integral após sequências de movimentos.
[ ] Memória do cache é limitada e observável.

## 4. Fase atual
Plan → Build → Verify.
