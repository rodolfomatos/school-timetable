# Ticket T055 — Fase 5: Consistencia das restrições S01–S10

## Contexto
CP-SAT e Python usam fórmulas e condições diferentes para S02, S05, S08, S09, S10; S03/S06 penalizam excessivamente; S07 usa domínio que impede violação em vez de penalizar; S04 cria variáveis duplicadas por slot.

## Objetivo
Definir formalmente S01–S10 e garantir que o avaliador Python e CP-SAT implementam a mesma semântica.

## Critérios de Aceitação
[ ] Todas as regras têm especificação formal aprovada.
[ ] Testes unitários cobrem fronteiras e contra-exemplos.
[ ] CP-SAT e Python concordam sobre a penalização em instâncias de teste controladas.
[ ] Reificações são bidireccionais quando necessário.
[ ] A matriz de restrições reflecte o estado real.
[ ] Nenhuma regra soft é acidentalmente transformada em hard.

## Fase atual
Plan → Build → Verify.
