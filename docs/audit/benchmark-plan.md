# Plano de Benchmarks — school-timetable

**Data:** 31 de outubro de 2026  
**Fase:** Fase 9 — Entregáveis (T045)

---

## 1. Objetivo

Estabelecer benchmarks padronizados para medir desempenho e qualidade do solver de horários escolares em diferentes tamanhos de instância.

---

## 2. Instâncias de Benchmark

| Instância | Turmas | Professores | Salas | Disciplinas | Slots/semana | Uso |
|-----------|--------|-------------|-------|-------------|--------------|-----|
| Pequena | 5 | 10 | 8 | 8 | 25 (5 dias × 5 horas) | Testes rápidos, desenvolvimento |
| Média | 20 | 40 | 25 | 15 | 25 | Validação de escala média |
| Grande | 60 | 120 | 70 | 25 | 25 | Teste de estresse |
| Complexa | 60+ | 120+ | 70+ | 25+ | 25+ | Múltiplos edifícios, laboratórios, módulos |

---

## 3. Métricas de Medição

| Métrica | Descrição |
|---------|-----------|
| Tempo até primeira solução viável | Tempo desde início até primeira solução sem violações duras |
| Taxa de viabilidade | % de execuções que encontram solução viável |
| Score por categoria | Penalidades por tipo de restrição mole (S01-S10) |
| Violações hard | Número de restrições duras violadas (deve ser 0 para soluções viáveis) |
| Tempo até melhor solução | Tempo desde início até melhor score encontrado |
| Gap de otimalidade | Diferença entre score atual e limite inferior (quando disponível) |
| Memória | Uso de RAM durante execução |
| Estabilidade entre seeds | Variação de score entre diferentes sementes aleatórias |

---

## 4. Planos de Execução

### 4.1 Execução Padrão
- 10 execuções por instância com sementes diferentes (1, 42, 123, 456, 789, 1024, 2048, 4096, 8192, 16384)
- Tempo limite: 60 segundos por execução
- Solver: Simulated Annealing, Tabu Search, CP-SAT (quando disponível)
- Relatório: média, desvio padrão, mínimo, máximo de cada métrica

### 4.2 Comparação de Algoritmos
- Executar CP-SAT, Simulated Annealing e Tabu Search nas mesmas instâncias
- Comparar qualidade (score), tempo e taxa de viabilidade
- Não afirmar superioridade sem resultados estatisticamente significativos

### 4.3 Benchmarks de Escalabilidade
- Testar com instâncias crescentes (pequena → média → grande)
- Medir degradação de desempenho com aumento do tamanho
- Identificar ponto de saturação (onde tempo > 60s sem solução viável)

---

## 5. Formato de Relatório

```
Benchmark: school-timetable v0.2.0
Data: 31/10/2026
Instância: pequena (5 turmas, 10 professores, 8 salas)
Tempo limite: 60 segundos
Execuções: 10

| Solver     | Tempo médio (s) | Score médio | Violações hard | Taxa viável |
|------------|-----------------|-------------|----------------|-------------|
| CP-SAT     | 12.5            | -45         | 0              | 100%        |
| Simulated Annealing | 8.2     | -52         | 0              | 100%        |
| Tabu Search | 6.8            | -58         | 0              | 100%        |

Estabilidade entre sementes: desvio padrão de score = 8.3
Memória pico: 245 MB
```

---

## 6. Critérios de Aceitação

- [ ] Tempo até primeira solução viável < 60 segundos para instância pequena
- [ ] Taxa de viabilidade ≥ 95% para instância pequena
- [ ] Zero violações duras em soluções marcadas como viáveis
- [ ] Resultados reproduzíveis (mesma semente = mesmo resultado)
- [ ] Benchmarks documentados com comandos para reprodução
