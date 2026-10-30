# Ticket T014 — Fix F-003: Restrições moles S04-S07 não implementadas

## Contexto
Finding F-003 (MAJOR): S04, S05, S06, S07 estão no catálogo mas não implementadas em `calcular_penalidades_moles`.

## Objetivo
Implementar as 4 restrições moles faltantes com testes unitários.

## Critérios de Aceitação
1. S04 (disciplinas não espalhadas) implementada.
2. S05 (padrão A-B-C-A) implementada.
3. S06 (duas horas para avaliação) implementada.
4. S07 (carga horária fora de limites) implementada.
5. Testes unitários para cada uma.
6. `make test` passa, `make lint` passa.

## Estado
**Concluído** (Plan → Build → Verify)

## Critérios de Aceitação — Status
1. S04 (disciplinas não espalhadas) implementada. — **OK**
2. S05 (padrão A-B-C-A) implementada. — **OK**
3. S06 (duas horas para avaliação) implementada. — **OK**
4. S07 (carga horária fora de limites) implementada. — **OK**
5. Testes unitários para cada uma. — **OK** (8 novos testes)
6. `make test` passa (73 testes), `make lint` passa. — **OK**

## Alterações
- `src/timetable/constraints.py`: implementadas S04, S05, S06, S07 em `calcular_penalidades_moles`
- `tests/test_constraints.py`: 8 novos testes para S04-S07

## Fase atual
Concluído.
