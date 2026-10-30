# Shadow Doc SD-BUILD-005 — Correção de Findings BLOCKER/MAJOR (T012, T013)

## Proveniência
Build phase dos tickets T012 e T013, concluídos em 2026-10-29.

## Corrigido — F-001 (BLOCKER): Tabu Search chave tabu sempre None

**Problema:** `chave_tabu` era sempre `None` no `tabu_search`, tornando a lista tabu inoperante.

**Correção em `src/timetable/local_search.py`:**
- `_gerar_vizinho_exchange` agora retorna `(vizinho, chave_tabu)` com chave gerada por `_chave_tabu_exchange(a1, a2)`
- `_gerar_vizinho_modify` agora retorna `(vizinho, chave_tabu)` com chave gerada por `_chave_tabu_modify(aula, novo_slot)`
- O loop principal do `tabu_search` usa as chaves retornadas para verificar `tabu_set` e aplicar critério de aspiração

## Corrigido — F-002 (MAJOR): tabu_set não sincronizado com deque

**Problema:** Quando a `deque` atingia `maxlen`, elementos antigos eram removidos automaticamente mas o `tabu_set` não era limpo, deixando chaves mortas.

**Correção em `src/timetable/local_search.py`:**
- Antes de `lista_tabu.append(chave_escolhida)`, verifica se `len(lista_tabu) == tamanho_tabu`
- Se sim, remove a chave mais antiga (`lista_tabu[0]`) do `tabu_set` com `tabu_set.discard(chave_antiga)`
- Após o append, adiciona a nova chave ao `tabu_set`

## Testes adicionados (6 novos)
- `test_chave_tabu_exchange_nao_e_none`
- `test_chave_tabu_modify_nao_e_none`
- `test_chaves_tabu_consistentes` (mesma troca = mesma chave, ordem independente)
- `test_gerar_vizinho_exchange_retorna_chave_tabu`
- `test_gerar_vizinho_modify_retorna_chave_tabu`
- `test_tabu_search_nao_entra_loop_infinito_com_tamanho_tabu_pequeno`
- `test_tabu_search_proporcao_exchange_um_usa_chaves`

## Cobertura
- `local_search.py`: 91% (era 81%)
- Total do projeto: 90.19%

## Escore epistémico
Alta confiança: as correções são diretas e verificáveis por testes unitários.

## Próximos passos
- T014: Implementar restrições moles S04-S07 (F-003, MAJOR)
- T015: Corrigir CP-SAT S09/S10 (F-004, F-005, MAJOR)
- T016: Avaliação incremental (F-006, MAJOR)
- T017: Findings MINOR (F-007 a F-011)
