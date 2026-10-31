# AES Plan Spec — T054 Fase 4: Semântica dos subgrupos

## 1. Sumário Executivo
Completar o suporte a subgrupos desde o modelo de domínio até aos operadores, validação, CP-SAT e persistência.

## 2. Objetivo
- Definir se uma sessão se aplica à turma inteira, a um subgrupo específico ou a vários subgrupos.
- Uma sessão de turma inteira conflita com qualquer sessão de um subgrupo da mesma turma no mesmo intervalo.
- Sessões de subgrupos distintos podem decorrer em paralelo apenas quando a regra pedagógica o permite e os recursos são distintos.
- Modelar uma actividade que se repete para cada subgrupo como sessões distintas relacionadas por um mesmo requirement/activity ID.
- Preservar subgrupo_id em todos os movimentos, clones, swaps, serialização e persistência.
- Rever a identidade das sessões para não colapsar subgrupos distintos.

## 3. Critérios de Aceitação
[ ] Turma inteira e subgrupo não podem sobrepor-se.
[ ] Subgrupos diferentes podem decorrer em paralelo quando permitido.
[ ] Uma actividade exigida para todos os subgrupos gera a cardinalidade correcta de sessões.
[ ] Move/Swap/clone preservam subgrupo_id e IDs de sessão.
[ ] Testes abrangem CP-SAT, Python validator, SA e Tabu.

## 4. Fase atual
Plan → Build → Verify.
