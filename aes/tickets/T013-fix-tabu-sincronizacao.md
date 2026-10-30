# Ticket T013 — Fix F-002: Tabu Search tabu_set não sincronizado

## Contexto
Finding F-002 (MAJOR): Quando a deque atinge maxlen, elementos antigos são removidos mas o `tabu_set` não é limpo, deixando chaves mortas.

## Objetivo
Sincronizar `tabu_set` com a `deque` quando elementos antigos são removidos.

## Critérios de Aceitação
1. Quando a deque remove um elemento antigo, ele também é removido de `tabu_set`.
2. Testes verificam que chaves saem da janela tabu e podem ser reutilizadas.
3. `make test` passa, `make lint` passa.

## Estado
**Concluído** (Plan → Build → Verify)

## Critérios de Aceitação — Status
1. Quando a deque remove um elemento antigo, ele também é removido de `tabu_set`. — **OK** (linhas 291-294: `chave_antiga = lista_tabu[0]`; `tabu_set.discard(chave_antiga)` antes do append)
2. Testes verificam que chaves saem da janela tabu e podem ser reutilizadas. — **OK** (teste `test_tabu_search_nao_entra_loop_infinito_com_tamanho_tabu_pequeno`)
3. `make test` passa (64 testes), `make lint` passa. — **OK**

## Alterações
- `src/timetable/local_search.py`: sincronização de `tabu_set` com `deque` antes de adicionar nova chave (remove chave mais antiga do set quando a deque está cheia)
- `tests/test_local_search.py`: teste de tamanho_tabu=1

## Fase atual
Concluído.
