# Shadow Doc SD-REVIEW-001 — Revisão Hostil (Peer Review)

## Proveniência
Review phase do ticket T009, concluída em 2026-10-29.

## Veredito Geral
**APROVADO COM CONDIÇÕES** — O projeto está estruturado corretamente seguindo os princípios AES, mas existem findings MAJOR que devem ser corrigidos antes de avançar para a fase Learn.

---

## Findings

### F-001 — Tabu Search: chave tabu sempre None (BLOCKER)

**Severidade:** BLOCKER

**Evidência:** `src/timetable/local_search.py`, linhas 247-252

```python
if rng.random() < proporcao_exchange:
    vizinho = _gerar_vizinho_exchange(atual, slots, rng)
    chave_tabu = None
else:
    vizinho = _gerar_vizinho_modify(atual, slots, rng)
    chave_tabu = None
```

As funções `_chave_tabu_exchange` e `_chave_tabu_modify` existem (linhas 100-112) mas **nunca são chamadas**. `chave_tabu` é sempre `None`, o que significa:

- Nenhum movimento é bloqueado pela lista tabu.
- O critério de aspiração nunca é testado.
- A lista tabu é inoperante — o Tabu Search degenera em busca gulosa simples.

**Condição de fechamento:** Chamar `_chave_tabu_exchange(a1, a2)` para movimentos de exchange e `_chave_tabu_modify(aula, novo_slot)` para movimentos de modify, passando as chaves geradas para a lógica de tabu.

---

### F-002 — Tabu Search: tabu_set não sincronizado com deque (MAJOR)

**Severidade:** MAJOR

**Evidência:** `src/timetable/local_search.py`, linhas 293-299

```python
if chave_escolhida is not None:
    lista_tabu.append(chave_escolhida)
    tabu_set.add(chave_escolhida)
    if len(lista_tabu) == tamanho_tabu and tamanho_tabu > 0:
        pass  # deque gerencia o tamanho; tabu_set pode conter chaves antigas
```

Quando a `deque` atinge `maxlen`, o elemento mais antigo é removido automaticamente, mas o `tabu_set` **não é limpo**. Chaves mortas permanecem no `tabu_set` para sempre, bloqueando movimentos que já deveriam estar fora da janela tabu.

**Condição de fechamento:** Quando a deque remove um elemento antigo, remover também do `tabu_set`. Alternativamente, usar apenas `deque` e verificar pertinência por iteração (O(tamanho_tabu)), ou reconstruir `tabu_set` a partir da deque quando necessário.

---

### F-003 — Restrições moles S04, S05, S06, S07 não implementadas (MAJOR)

**Severidade:** MAJOR

**Evidência:** `src/timetable/constraints.py`, função `calcular_penalidades_moles` (linhas 130-241)

O catálogo de restrições (`docs/constraints.md`) lista 10 restrições moles (S01-S10), mas apenas **6 estão implementadas** (S01, S02, S03, S08, S09, S10). As seguintes estão em falta:

- **S04:** Disciplinas não espalhadas pela semana (bloco único)
- **S05:** Padrão A-B-C-A (mesma disciplina interrompida)
- **S06:** Falta de duas horas consecutivas para avaliação
- **S07:** Carga horária do professor fora dos limites

**Impacto:** A função objetivo não penaliza essas restrições, o que significa que o solver pode produzir horários que violam essas regras sem qualquer penalidade.

**Condição de fechamento:** Implementar S04, S05, S06, S07 em `calcular_penalidades_moles` com testes unitários correspondentes.

---

### F-004 — CP-SAT: S09 penaliza diferença sempre, não apenas quando > 2 (MAJOR)

**Severidade:** MAJOR

**Evidência:** `src/timetable/cp_sat_baseline.py`, linhas 257-263

```python
diff_var = model.NewIntVar(0, len(slots), f"diff_{disc_id}")
model.Add(diff_var == max_var - min_var)
termos_objetivo.append((diff_var, 11))
```

A variável `diff_var` é adicionada ao objetivo com peso 11, mas não há nenhuma constraint que defina que a penalidade só se aplica quando `diff_var > 2`. Isso penaliza soluções onde a diferença é 0, 1 ou 2 (que são aceitáveis), distorcendo a função objetivo.

**Condição de fechamento:** Adicionar uma variável booleana ou usar `model.Add(diff_var > 2).OnlyEnforceIf(penaliza)` para penalizar apenas quando a diferença excede 2.

---

### F-005 — CP-SAT: S10 penaliza qualquer concentração, não apenas >= 5 aulas (MAJOR)

**Severidade:** MAJOR

**Evidência:** `src/timetable/cp_sat_baseline.py`, linhas 273-281

```python
var_dia_count = model.NewIntVar(0, len(slots), f"countday_{prof_id}_{dia}")
model.Add(var_dia_count == sum(...))
termos_objetivo.append((var_dia_count, 10))
```

A variável `var_dia_count` conta o número de aulas de um professor num dia, mas é penalizada sempre com peso 10, independentemente de haver 1 ou 5 aulas. A restrição S07/S10 deveria penalizar apenas quando há concentração excessiva (>= 5 aulas num dia, ou carga fora dos limites).

**Condição de fechamento:** Adicionar uma variável booleana que se ative apenas quando `var_dia_count >= 5` (ou quando a carga semanal está fora de `[carga_minima, carga_maxima]`), e penalizar apenas essa variável.

---

### F-006 — Avaliação não incremental (MAJOR)

**Severidade:** MAJOR

**Evidência:** `src/timetable/local_search.py` e `src/timetable/objective.py`

Cada iteração da metaheurística chama `avaliar(vizinho, ctx)`, que executa `verificar_hard` (O(n) sobre todas as aulas) e `calcular_penalidades_moles` (O(n) sobre todas as aulas). Para milhares de iterações com dezenas de aulas, isso é aceitável, mas para instâncias maiores (centenas de aulas) torna-se um gargalo.

**Impacto:** Performance degradada em instâncias reais de escola.

**Condição de fechamento:** Implementar avaliação incremental (recalcular apenas as penalidades afetadas pelo movimento de troca/movimento) ou documentar que a abordagem atual é adequada apenas para instâncias pequenas/médias.

---

### F-007 — S03: lógica de horas consecutivas complexa e ofuscada (MINOR)

**Severidade:** MINOR

**Evidência:** `src/timetable/constraints.py`, linhas 170-175

```python
tem_consecutivas = any(
    (dia == slots_ordenados[i][0] and hora == slots_ordenados[i][1] + 1)
    for i in range(len(slots_ordenados) - 1)
    for dia, hora in [slots_ordenados[i + 1]]
)
```

A expressão `for dia, hora in [slots_ordenados[i + 1]]` é desnecessariamente complexa e ofuscada. Pode ser simplificada para melhorar a legibilidade e manutenibilidade.

**Condição de fechamento:** Refatorar para uma expressão mais clara, por exemplo:

```python
tem_consecutivas = any(
    slots_ordenados[i][0] == slots_ordenados[i + 1][0]
    and slots_ordenados[i][1] + 1 == slots_ordenados[i + 1][1]
    for i in range(len(slots_ordenados) - 1)
)
```

---

### F-008 — UI: mover_aula/trocar_aulas não verificam conflitos de restrições duras (MINOR)

**Severidade:** MINOR

**Evidência:** `src/timetable/ui.py`, funções `mover_aula` e `trocar_aulas`

A UI permite mover/trocar aulas sem verificar se o movimento cria conflitos (professor em dois lugares ao mesmo tempo, sala ocupada, etc.). O utilizador só descobre a violação ao chamar `validar_apos_movimento` separadamente.

**Condição de fechamento:** Adicionar um parâmetro opcional `validar: bool = True` a `mover_aula` e `trocar_aulas` que, quando True, executa `verificar_hard` e rejeita o movimento se criar violações duras. Ou documentar que o utilizador deve sempre chamar `validar_apos_movimento` após cada edição.

---

### F-009 — Importação JSON sem validação de estrutura (MINOR)

**Severidade:** MINOR

**Evidência:** `src/timetable/ui.py`, função `importar_json` (linhas 36-53)

```python
dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
aulas = [
    Aula(
        turma=item["turma"],
        ...
        slot=Slot(dia=item["slot"]["dia"], hora=item["slot"]["hora"]),
    )
    for item in dados.get("aulas", [])
]
```

Se o JSON estiver mal formado (campos obrigatórios em falta, tipos errados), a função lança `KeyError` ou `TypeError` não tratados, em vez de um erro descritivo.

**Condição de fechamento:** Adicionar validação de estrutura obrigatória (campos `turma`, `disciplina`, `professor`, `sala`, `slot.dia`, `slot.hora`) com erro descritivo quando campos estão em falta.

---

### F-010 — Teste de integração não verifica qualidade real (MINOR)

**Severidade:** MINOR

**Evidência:** `tests/test_integration.py`, linhas 68-90

Os testes de integração apenas verificam que `av.score >= -1_000_000` (não é -infinito absoluto), sem verificar se as restrições duras são realmente respeitadas ou se a qualidade melhora.

**Condição de fechamento:** Adicionar verificação de `verificar_hard(resultado, ctx) == []` nos testes de integração, e opcionalmente verificar que o score não piorou em relação ao inicial.

---

### F-011 — `_chave_tabu_exchange` parâmetro `slots_disponiveis` não usado (MINOR)

**Severidade:** MINOR

**Evidência:** `src/timetable/local_search.py`, linhas 31-35

A função `_gerar_vizinho_exchange` recebe `slots_disponiveis` mas não o usa (troca slots entre aulas existentes, não gera novos slots). Isso é inconsistente com a assinatura de `_gerar_vizinho_modify` que sim o usa.

**Condição de fechamento:** Remover o parâmetro não usado de `_gerar_vizinho_exchange` ou usá-lo de forma consistente.

---

## Resumo de Severidade

| ID | Severidade | Descrição | Estado |
|----|-----------|-----------|--------|
| F-001 | BLOCKER | Tabu Search: chave tabu sempre None | Pendente |
| F-002 | MAJOR | Tabu Search: tabu_set não sincronizado | Pendente |
| F-003 | MAJOR | Restrições moles S04-S07 não implementadas | Pendente |
| F-004 | MAJOR | CP-SAT: S09 penaliza sem condição > 2 | Pendente |
| F-005 | MAJOR | CP-SAT: S10 penaliza sem condição >= 5 | Pendente |
| F-006 | MAJOR | Avaliação não incremental | Pendente |
| F-007 | MINOR | S03 lógica ofuscada | Pendente |
| F-008 | MINOR | UI: sem verificação de conflitos | Pendente |
| F-009 | MINOR | JSON: sem validação de estrutura | Pendente |
| F-010 | MINOR | Testes de integração fracos | Pendente |
| F-011 | MINOR | Parâmetro não usado | Pendente |

**Total:** 1 BLOCKER, 5 MAJOR, 5 MINOR

---

## Próximos Passos

1. Corrigir F-001 (BLOCKER) antes de avançar para Learn.
2. Corrigir F-002 a F-006 (MAJOR) antes de avançar para Learn.
3. F-007 a F-011 (MINOR) podem ser adiados para backlog ou corrigidos oportunisticamente.
4. Após correção, atualizar este shadow doc com o status de cada finding.
5. Criar tickets no kanban para cada finding corrigido.
