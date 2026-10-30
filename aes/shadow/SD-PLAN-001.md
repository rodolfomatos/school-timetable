# Shadow Doc SD-PLAN-001 — Decisões de Planeamento (T001)

## Proveniência
Extraído da planificação inicial do projeto school-timetable, com base na revisão da literatura fornecida pelo utilizador e na prática AES.

## Pontos Decididos
1. **Linguagem:** Python 3.11+ (facilita prototipagem e uso de OR-Tools).
2. **Abordagem principal:** Busca local (Tabu Search / Simulated Annealing), não GA puro.
3. **Função objetivo:** Soma aditiva de penalidades (evitar produto multiplicativo).
4. **Seed:** Horário parcial imutável (~30% dos slots) para reduzir espaço de busca.
5. **Linha de base exata:** OR-Tools CP-SAT para validação de viabilidade em instâncias pequenas.
6. **Interface:** Ajuste manual tipo "insets de plástico" (adiado para T007).

## Pontos em Aberto
- Escolha final da biblioteca de CP-SAT.
- Formato de exportação do horário (JSON, CSV, iCal?).

## Escore Epistémico
Alta confiança nas decisões de algoritmos (baseadas em ITC 2007 e surveys). Média confiança na escolha de bibliotecas específicas (não testado ainda).
