# Shadow Doc SD-LEARN-002 — Aprendizados Consolidados (Fase Learn)

## Proveniência
Fase Learn do AES, executada em 30/10/2026, após conclusão de todos os 17 tickets e correção de 11 findings do review hostil.

## Aprendizados Técnicos

### 1. Função objetivo aditiva vs. multiplicativa
**Decisão:** Usar sempre soma aditiva de penalidades, nunca produto multiplicativo.
**Evidência:** O trabalho acadêmico citado na literatura usou produto multiplicativo com `gmp` (números de 10⁻²⁰⁰ a 10³⁰⁰) — totalmente ineficiente. A abordagem aditiva (score = -Σ penalidade × peso) é legível, ajustável e não sofre de explosão numérica.
**Escore epistémico:** Alta confiança. Validado por testes e literatura (Wilke & Ostler 2008, ITC 2007).

### 2. Metaheurísticas de busca local batem GA puro
**Decisão:** Usar Tabu Search e Simulated Annealing como motores principais.
**Evidência:** ITC 2007 mostrou que metaheurísticas de busca local bateram algoritmos genéticos puros. Wilke & Ostler (2008) concluiu que SA tem o melhor tradeoff custo/qualidade.
**Escore epistémico:** Alta confiança. Consenso da comunidade de timetabling.

### 3. Seed parcial imutável reduz drasticamente o espaço de busca
**Decisão:** Preencher ~30% dos slots com horário viável e imutável antes da busca.
**Evidência:** Estratégia recomendada na literatura para redução do espaço de soluções. Implementada em `seed.py` e respeitada por todos os operadores de busca local e UI.
**Escore epistémico:** Média confiança. Funciona bem em testes, não validado com dados reais de escola grande.

### 4. Slots imutáveis devem ser respeitados em TODO operador
**Decisão:** Todos os operadores (exchange, modify, UI manual) verificam `horario.slots_imutaveis`.
**Evidência:** Encontrado durante o review hostil — sem isso, o seed seria destruído pela busca.
**Escore epistémico:** Alta confiança. Testado explicitamente.

### 5. Chaves de tabu devem ser geradas explicitamente
**Decisão:** `_gerar_vizinho_exchange` e `_gerar_vizinho_modify` retornam `(vizinho, chave_tabu)`.
**Evidência:** Finding F-001 (BLOCKER) — sem chaves reais, a lista tabu é inoperante.
**Escore epistémico:** Alta confiança. Corrigido e testado.

### 6. Cache de avaliação melhora performance sem complexidade excessiva
**Decisão:** Adicionado `_cache_avaliacao` em `objective.py` em vez de avaliação incremental completa.
**Evidência:** Finding F-006 (MAJOR) — avaliação completa O(n) por iteração é um gargalo para instâncias grandes. O cache é um meio-termo pragmático.
**Escore epistémico:** Média confiança. Ajuda em horários repetidos, não resolve o problema fundamental de complexidade.

### 7. Fatores humanos exigem satisficing, não otimalidade
**Decisão:** O objetivo é "bom o suficiente" (satisficing), não 100% ótimo.
**Evidência:** Comentário do utilizador sobre professores, carga ao longo do tempo, justiça percebida. Implementado via restrições S08-S10 e score_alvo nas metaheurísticas.
**Escore epistémico:** Alta confiança. Corroborado pela literatura de timetabling real-world.

## Arquitetura Final do Código

```
src/timetable/
├── models.py        # Slot, Sala, Professor, Turma, Disciplina, Aula, Horario
├── constraints.py   # H01-H08 (duras) + S01-S10 (moles, aditivas)
├── objective.py     # avaliar(), avaliar_com_cache(), cache de avaliação
├── seed.py          # Seed parcial imutável (~30% dos slots)
├── solver.py        # Interface SolverBase
├── cp_sat_baseline.py  # OR-Tools CP-SAT (opcional, com fallback)
├── local_search.py  # Tabu Search + Simulated Annealing (com chaves de tabu)
└── ui.py            # Grade, mover/trocar/remover, validação JSON, exportação
```

## Métricas Finais

| Métrica | Valor |
|---------|-------|
| Testes totais | 80 |
| Testes passando | 80 |
| Cobertura total | 90.90% |
| Gate de cobertura (≥ 80%) | ✅ Atingido |
| Erros de lint | 0 |
| Erros de format | 0 |
| Findings do review hostil | 11 (1 BLOCKER, 5 MAJOR, 5 MINOR) |
| Findings corrigidos | 11 (100%) |
| Tickets no kanban | 17 (todos Concluído) |

## Decisões Arquiteturais para o Futuro

1. **Or-Tools CP-SAT é opcional:** O projeto roda sem ele (fallback graceful). Para instâncias pequenas, é uma linha de base exata valiosa.
2. **UI é biblioteca, não framework:** `ui.py` expõe funções puras (sem dependência de framework específico). Fácil de adaptar para CLI, TUI ou web posteriormente.
3. **Satisficing é o modelo mental:** O utilizador humano deve poder ajustar o resultado final. A UI suporta isso via `validar=True` e `listar_aulas_mutaveis/imutaveis`.

## Recomendações para T018+

- **T018:** Executar com dados reais de escola (validar escala e performance)
- **T019:** Interface de linha de comando (CLI) para uso por não-programadores
- **T020:** Exportação para iCal/CSV para integração com sistemas escolares existentes
- **T021:** Testes de propriedade (property-based testing) para validar restrições duras em aleatório
