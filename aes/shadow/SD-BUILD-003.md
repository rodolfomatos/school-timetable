# Shadow Doc SD-BUILD-003 — Metaheurística Refinada (T005)

## Proveniência
Build phase do ticket T005, concluída em 2026-10-29.

## O que foi construído
Refinação completa de `src/timetable/local_search.py` com:

### Operadores de movimento
- **Exchange** (trocar slots de duas aulas) — movimento principal, 70% dos vizinhos. Mais comum que modify segundo a literatura (trabalho de GA citado, ITC 2007).
- **Modify** (mover uma aula para outro slot) — movimento secundário, 30% dos vizinhos.

### Respeito a slots imutáveis
Ambos os operadores verificam `horario.slots_imutaveis` e não alteram aulas cujos slots estejam no seed (T006). Se não houver aulas mutáveis suficientes, devolvem None.

### Critério de parada (satisficing, T011)
- `tempo_limite_segundos`: tempo máximo de execução.
- `iteracoes_sem_melhoria_limite`: parar se não houver melhoria no score global após N iterações (default 500).
- `score_alvo`: parar se o score atingir este valor (satisficing — "bom o suficiente").

### Lista tabu
- Implementada como `collections.deque` com `maxlen=tamanho_tabu` (FIFO adequado).
- Critério de aspiração: aceita movimento tabu se melhora o score global.

### Simulated Annealing
- Temperatura inicial configurável (default 1000.0).
- Resfriamento geométrico (default 0.995).
- Critério de aceitação: aceita se melhor, ou com probabilidade `exp(delta/temperatura)` se pior.
- Semente opcional para reprodutibilidade.

### Testes
17 testes específicos de metaheurística (45 no total no projeto).
Cobertura do ficheiro local_search.py: 81%.

## Decisões de design
1. Exchange como movimento principal (70%) baseado na literatura.
2. Semente opcional para reprodutibilidade dos resultados.
3. Critério de parada por não-melhoria evita loops infinitos.
4. Slots imutáveis respeitados para preservar o seed parcial (T006).

## Escore epistémico
Alta confiança na escolha de operadores (baseada em ITC 2007 e Wilke & Ostler 2008). Média confiança nos parâmetros padrão (temperatura, tamanho tabu) — não otimizados para dados reais de escola ainda.

## Próximos passos
- T007: Interface de ajustamento manual ("insets de plástico").
- T009: Revisão hostil (peer review).
