# Arquitetura de Software

## Camadas
1. **Modelo de domínio** (`models.py`) — dataclasses imutáveis onde possível.
2. **Restrições** (`constraints.py`) — verificações hard e soft.
3. **Objetivo** (`objective.py`) — função objetivo aditiva.
4. **Seed** (`seed.py`) — geração de horário parcial imutável.
5. **Solver** (`solver.py`) — interface abstrata; implementações: CP-SAT (baseline), Tabu Search, Simulated Annealing (`local_search.py`).
6. **UI** (`ui.py`) — ajustamento manual (insets de plástico).

## Fluxo de Dados
```
dados_entrada (JSON)
   ↓
Modelo de domínio (turmas, professores, salas, slots)
   ↓
Seed parcial (30% dos slots, imutável)
   ↓
Solver (metaheurística ou CP-SAT)
   ↓
Horário completo (com ou without violações moles)
   ↓
UI de ajuste manual (opcional)
   ↓
Exportação (JSON/CSV)
```

## Princípios
- Restrições duras = condição de viabilidade (binária).
- Restrições moles = penalidade aditiva na função objetivo.
- Avaliação incremental: ao trocar duas aulas, recalcular apenas as penalidades afetadas.
- Nenhum código sem ticket AES associado.
