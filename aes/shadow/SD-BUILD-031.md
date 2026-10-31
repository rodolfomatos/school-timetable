# Shadow Doc SD-BUILD-030 — T055 Fase 5: Consistencia das restrições S01–S10

## Proveniência
Fase 5 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Definir formalmente S01–S10 e garantir que o avaliador Python e CP-SAT implementam a mesma semântica.

## Decisões tomadas
- Para cada restrição documentar: definição matemática, entidades e janela temporal abrangidas, unidade da penalização, limites e parâmetros configuráveis, casos de fronteira, e se é preferência, objectivo ou requisito hard.
- Rever especificamente: S02, S03/S06, S04, S05, S07, S08, S09, S10.
- Se for soft, a variável de carga não pode ter domínio que torne a violação impossível; usar variável de excesso/reificação correcta.
- Reificações são bidireccionais quando necessário.
- Nenhuma regra soft é acidentalmente transformada em hard.

## Escore epistémico
Alta confiança — baseada na literatura de timetabling e na análise das restrições existentes.

## Próximos passos
- T056: Cache e avaliação incremental
