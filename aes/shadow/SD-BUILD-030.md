# Shadow Doc SD-BUILD-029 — T054 Fase 4: Semântica dos subgrupos

## Proveniência
Fase 4 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Completar o suporte a subgrupos desde o modelo de domínio até aos operadores, validação, CP-SAT e persistência.

## Decisões tomadas
- Definir se uma sessão se aplica à turma inteira, a um subgrupo específico ou a vários subgrupos.
- Uma sessão de turma inteira conflita com qualquer sessão de um subgrupo da mesma turma no mesmo intervalo.
- Sessões de subgrupos distintos podem decorrer em paralelo apenas quando a regra pedagógica o permite e os recursos são distintos.
- Modelar uma actividade que se repete para cada subgrupo como sessões distintas relacionadas por um mesmo requirement/activity ID.
- Preservar subgrupo_id em todos os movimentos, clones, swaps, serialização e persistência.
- Rever a identidade das sessões para não colapsar subgrupos distintos.

## Escore epistémico
Alta confiança — baseada na análise do modelo de domínio e na literatura de timetabling.

## Próximos passos
- T055: Consistencia das restrições S01–S10
