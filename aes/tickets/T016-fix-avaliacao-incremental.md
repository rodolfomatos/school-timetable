# Ticket T016 — Fix F-006: Avaliação não incremental

## Contexto
Finding F-006 (MAJOR): Cada iteração da metaheurística reavalia TODO o horário (O(n)), sem avaliação incremental.

## Objetivo
Implementar avaliação incremental ou documentar que a abordagem atual é adequada apenas para instâncias pequenas/médias.

## Critérios de Aceitação
1. Avaliação incremental implementada OU documentação de limitação adicionada.
2. Se implementada: testes verificam que o resultado é equivalente à avaliação completa.
3. `make test` passa, `make lint` passa.

## Estado
**Concluído** (Plan → Build → Verify)

## Critérios de Aceitação — Status
1. Documentação de limitação de performance adicionada ao código. — **OK** (docstring em `avaliar` e comentário em `local_search.py`)
2. Cache de avaliação adicionado para evitar recálculo de horários repetidos. — **OK** (`_cache_avaliacao` em `objective.py`)
3. Testes verificam que o cache funciona. — **OK** (teste de cache no test_objective.py)
4. `make test` passa, `make lint` passa. — **OK**

## Alterações — Status
1. Documentação de limitação de performance adicionada ao código. — **OK** (docstring em `objective.py` e comentário em `local_search.py`)
2. Cache de avaliação adicionado para evitar recálculo de horários repetidos. — **OK** (`_cache_avaliacao`, `avaliar_com_cache`, `limpar_cache_avaliacao` em `objective.py`)
3. Testes verificam que o cache funciona. — **OK** (2 novos testes em `test_objective.py`)
4. `make test` passa (78 testes), `make lint` passa. — **OK**

## Alterações
- `src/timetable/objective.py`: adicionado `_cache_avaliacao` (dict), `avaliar_com_cache()`, `limpar_cache_avaliacao()`, `_chave_horario()`
- `src/timetable/local_search.py`: comentário documentando a limitação de performance da avaliação completa
- `tests/test_objective.py`: 2 novos testes para cache de avaliação

## Fase atual
Concluído.
