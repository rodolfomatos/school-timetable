# Ticket T005 — Metaheurística principal (Tabu Search / Simulated Annealing)

## Contexto
O problema de horário escolar é NP-hard. A literatura (ITC 2007, Wilke & Ostler 2008) mostra que metaheurísticas de busca local (Tabu Search, Simulated Annealing) batem algoritmos genéticos puros. A implementação atual em `local_search.py` é um esqueleto que precisa de refinamento:

- Movimento de "exchange" (trocar duas aulas) deve ser mais comum que "modify" (substituir professor/sala)
- Deve respeitar slots imutáveis do seed (T006)
- Deve incorporar critério de parada "bom o suficiente" (satisficing, T011)
- Lista tabu deve ser gerida como FIFO adequado, não `set.pop()`

## Objetivo
Refinar `local_search.py` com:
1. Operador de "exchange" (trocar slot de duas aulas) como movimento principal
2. Operador de "modify" (mover uma aula para outro slot) como movimento secundário
3. Respeito a slots imutáveis do seed (não alterar aulas em slots imutáveis)
4. Critério de parada por "bom o suficiente" (score não melhora após N iterações, ou score ≥ limiar satisficing)
5. Lista tabu FIFO adequada com critério de aspiração
6. Simulated Annealing com resfriamento geométrico adequado

## Critérios de Aceitação
1. `make test` passa (incluindo novos testes de metaheurística).
2. `make lint` passa sem erros.
3. O solver respeita slots imutáveis (não altera aulas do seed).
4. O operador de exchange é implementado e usado.
5. Critério de parada por não-melhoria está implementado.
6. Nenhuma restrição dura é violada na solução de saída (quando viável).

## Riscos (Hostile Analysis)
- Loop infinito se não houver vizinhos válidos → mitigação: tempo limite + limite de iterações sem melhoria.
- Qualidade depende dos parâmetros (temperatura, tamanho tabu) → mitigação: valores padrão razoáveis, configuráveis.
- Performance com muitos slots → mitigação: avaliação incremental ou limitar número de vizinhos avaliados.

## Estado
**Concluído** (Plan → Build → Verify)

## Critérios de Aceitação — Status
1. `make test` passa (45 testes, incluindo metaheurística refinada). — **OK**
2. `make lint` passa sem erros. — **OK**
3. O solver respeita slots imutáveis (não altera aulas do seed). — **OK** (testes test_simulated_annealing_respeita_imutaveis, test_tabu_search_respeita_imutaveis)
4. O operador de exchange é implementado e usado. — **OK** (_gerar_vizinho_exchange, proporção 70%)
5. Critério de parada por não-melhoria está implementado. — **OK** (iteracoes_sem_melhoria_limite)
6. Nenhuma restrição dura é violada na solução de saída (quando viável). — **OK** (testes de não-violação hard)

## Fase atual
Concluído. Próximo: T007 (Interface de ajuste manual) ou T009 (Revisão hostil).
