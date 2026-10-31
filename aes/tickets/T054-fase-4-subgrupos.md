# Ticket T054 — Fase 4: Semântica dos subgrupos

## Contexto
Subgrupos não são preservados nos movimentos locais; H03 permite sobreposição entre turma inteira e subgrupo; sessões de subgrupo não são modeladas como sessões distintas relacionadas.

## Objetivo
Completar o suporte a subgrupos desde o modelo de domínio até aos operadores, validação, CP-SAT e persistência.

## Critérios de Aceitação
[ ] Turma inteira e subgrupo não podem sobrepor-se.
[ ] Subgrupos diferentes podem decorrer em paralelo quando permitido.
[ ] Uma actividade exigida para todos os subgrupos gera a cardinalidade correcta de sessões.
[ ] Move/Swap/clone preservam subgrupo_id e IDs de sessão.
[ ] Testes abrangem CP-SAT, Python validator, SA e Tabu.

## Fase atual
Plan → Build → Verify.
