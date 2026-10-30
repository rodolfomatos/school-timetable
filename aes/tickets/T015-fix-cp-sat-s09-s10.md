# Ticket T015 — Fix F-004 e F-005: CP-SAT S09/S10 penalização sem condição

## Contexto
Finding F-004 (MAJOR): S09 penaliza diferença sempre, não apenas quando > 2.
Finding F-005 (MAJOR): S10 penaliza qualquer concentração, não apenas >= 5 aulas.

## Objetivo
Adicionar condições às penalidades S09 e S10 no CP-SAT para que apenas penalizem quando excedem o limiar.

## Critérios de Aceitação
1. S09 penaliza apenas quando `diff_var > 2`.
2. S10 penaliza apenas quando `var_dia_count >= 5` (ou carga fora dos limites).
3. Testes verificam o comportamento correto.
4. `make test` passa, `make lint` passa.

## Estado
**Concluído** (Plan → Build → Verify)

## Critérios de Aceitação — Status
1. S09 penaliza apenas quando `diff_var > 2`. — **OK** (variável booleana `penaliza_s09` com `OnlyEnforceIf`)
2. S10 penaliza apenas quando `var_dia_count >= 5`. — **OK** (variável booleana `penaliza_s10` com `OnlyEnforceIf`)
3. Testes verificam o comportamento correto. — **OK** (3 novos testes CP-SAT)
4. `make test` passa (76 testes), `make lint` passa. — **OK**

## Alterações
- `src/timetable/cp_sat_baseline.py`: S09 agora usa variável booleana com `model.Add(diff_var > 2).OnlyEnforceIf(penaliza_s09)`; S10 usa `model.Add(var_dia_count >= 5).OnlyEnforceIf(penaliza_s10)`
- `tests/test_cp_sat.py`: 3 novos testes para S09/S10 com condição de limiar

## Fase atual
Concluído.
