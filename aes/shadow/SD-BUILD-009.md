# Shadow Doc SD-BUILD-009 — Correções Findings MINOR (T017)

## Proveniência
Build phase do ticket T017, concluída em 2026-10-29. Corrigi F-007 a F-011 (MINOR).

## Corrigido — F-007 (MINOR): S03 lógica ofuscada

**Problema:** Expressão complexa e ofuscada para detetar horas consecutivas.

**Correção em `src/timetable/constraints.py`:**
- Substituída a expressão `for dia, hora in [slots_ordenados[i + 1]]` por comparação direta de índices:
  ```python
  slots_ordenados[i][0] == slots_ordenados[i + 1][0]
  and slots_ordenados[i][1] + 1 == slots_ordenados[i + 1][1]
  ```

## Corrigido — F-008 (MINOR): UI sem verificação de conflitos

**Problema:** `mover_aula` e `trocar_aulas` não verificavam restrições duras após o movimento.

**Correção em `src/timetable/ui.py`:**
- Adicionado parâmetro `validar: bool = False` a ambas as funções
- Adicionado parâmetro `ctx: ContextoRestricoes | None = None`
- Quando `validar=True` e `ctx` fornecido, executa `verificar_hard` e devolve horário inalterado se houver violações

## Corrigido — F-009 (MINOR): JSON sem validação de estrutura

**Problema:** `importar_json` lançava `KeyError`/`TypeError` não tratados para JSON mal formado.

**Correção em `src/timetable/ui.py`:**
- Adicionada função `_validar_estrutura_json(dados)` que verifica campos obrigatórios
- Campos validados: `turma`, `disciplina`, `professor`, `sala`, `slot.dia`, `slot.hora`
- Levanta `ValueError` com mensagem descritiva quando campos estão em falta

## Corrigido — F-010 (MINOR): Testes de integração fracos

**Problema:** Testes de integração apenas verificavam `score >= -1_000_000`.

**Correção em `tests/test_integration.py`:**
- Adicionada verificação de `verificar_hard(resultado, ctx) == []` em ambos os testes
- Importação de `verificar_hard` adicionada

## Corrigido — F-011 (MINOR): Parâmetro não usado

**Problema:** `slots_disponiveis` não usado em `_gerar_vizinho_exchange`.

**Correção em `src/timetable/local_search.py`:**
- Renomeado para `_slots_disponiveis` (convenção Python para parâmetro não usado)
- Adicionado comentário explicativo no docstring

## Testes adicionados (2 novos)
- `test_importar_json_campo_obrigatorio_em_falta_levanta_erro`
- `test_importar_json_slot_campo_em_falta_levanta_erro`

## Cobertura
- Total do projeto: 90.90%
- `ui.py`: 85%

## Escore epistémico
Alta confiança: todas as correções são diretas e verificáveis por testes unitários.

## Estado final do review hostil
Todos os 11 findings do SD-REVIEW-001 foram tratados:
- F-001 (BLOCKER): Corrigido (T012)
- F-002 a F-006 (MAJOR): Corrigidos (T013-T016)
- F-007 a F-011 (MINOR): Corrigidos (T017)

O projeto está pronto para avançar para a fase Learn (T010 já concluído).
