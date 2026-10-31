# Shadow Doc SD-BUILD-019 — Fase 5: Objetivo e Metaheurísticas (T041)

## Proveniência
Fase 5 do plano de auditoria (DOCX seção 11), concluída em 31/10/2026.

## O que foi construído

### objective.py
- Função objetivo aditiva: score = -soma(penalidades moles)
- `Avaliacao` dataclass com: viável, violações_hard, penalidades_moles, score
- `MUITO_NEGATIVO = -1_000_000` para soluções inviáveis
- `avaliar_com_cache()` com cache por chave de horário
- `limpar_cache_avaliacao()` para limpar entre execuções

### local_search.py
- `simulated_annealing()`: temperatura inicial, resfriamento geométrico, critério de aceitação exp(delta/temperatura)
- `tabu_search()`: lista tabu FIFO, critério de aspiração, movimentos de troca e modificação
- Operadores respeitam slots imutáveis (seed)
- Semente opcional para reprodutibilidade
- Critério de parada por tempo limite e iterações sem melhoria

## Decisões tomadas
- Função objetivo aditiva (não multiplicativa) conforme recomendado na literatura
- Priorização: restrições duras têm score muito negativo, moles têm penalidade aditiva
- Critério de aspiração no Tabu Search: aceita movimento tabu se melhora o global
- Semente opcional para reprodutibilidade de resultados

## Escore epistémico
Alta confiança — baseado na literatura (ITC 2007, Wilke & Ostler 2008) e na documentação de auditoria.

## Próximos passos
- T042: Avaliação incremental com cache isolado por instância de problema
- T043: Backend e operação (solver assíncrono, migrações Alembic, segurança)
- T044: Testes e benchmarks
