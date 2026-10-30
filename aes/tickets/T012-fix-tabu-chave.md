# Ticket T012 — Fix F-001: Tabu Search chave tabu sempre None

## Contexto
Finding F-001 (BLOCKER): `chave_tabu` é sempre `None` no `tabu_search`, tornando a lista tabu inoperante.

## Objetivo
Chamar `_chave_tabu_exchange` e `_chave_tabu_modify` para gerar chaves de tabu reais e usá-las na lógica de bloqueio/aspiração.

## Critérios de Aceitação
1. `chave_tabu` não é mais sempre `None` para movimentos de exchange.
2. `chave_tabu` não é mais sempre `None` para movimentos de modify.
3. Testes verificam que a lista tabu bloqueia movimentos repetidos.
4. `make test` passa, `make lint` passa.

## Estado
**Concluído** (Plan → Build → Verify)

## Critérios de Aceitação — Status
1. `chave_tabu` não é mais sempre `None` para movimentos de exchange. — **OK** (`_chave_tabu_exchange` chamado na linha 248)
2. `chave_tabu` não é mais sempre `None` para movimentos de modify. — **OK** (`_chave_tabu_modify` chamado na linha 251)
3. Testes verificam que a lista tabu bloqueia movimentos repetidos. — **OK** (novos testes de chave tabu)
4. `make test` passa (64 testes), `make lint` passa. — **OK**

## Alterações
- `src/timetable/local_search.py`: `_gerar_vizinho_exchange` e `_gerar_vizinho_modify` agora retornam `(vizinho, chave_tabu)` com chaves geradas por `_chave_tabu_exchange` e `_chave_tabu_modify`
- `tests/test_local_search.py`: 6 novos testes para chaves de tabu

## Fase atual
Concluído.
