# Shadow Doc SD-BUILD-031 — T056 Fase 6: Cache e avaliação incremental

## Proveniência
Fase 6 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Corrigir a contaminação do cache entre contextos e clarificar a diferença entre cache integral e avaliação incremental.

## Decisões tomadas
- Incluir na chave do cache a identidade/versão do ProblemInstance e do ConstraintProfile.
- Incluir todos os elementos relevantes da solução, incluindo subgrupo e identidade da sessão.
- Preferir cache scoped à execução/instância em vez de dicionário global.
- Definir limite de memória e política de eviction.
- Renomear documentação: cache de resultados não é avaliação incremental.
- Só implementar avaliação incremental quando houver cálculo de deltas por restrição e validação contra cálculo integral.

## Escore epistémico
Alta confiança — baseada na análise de caching e avaliação incremental.

## Próximos passos
- T057: SolverResult e jobs persistentes
