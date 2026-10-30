# Shadow Doc SD-BUILD-007 — Correção CP-SAT S09/S10 (T015)

## Proveniência
Build phase do ticket T015, concluída em 2026-10-29. Corrigi F-004 e F-005 (MAJOR).

## Corrigido — F-004 (MAJOR): CP-SAT S09 penaliza diferença sempre

**Problema:** `diff_var` (diferença entre max e min de aulas por professor numa disciplina) era penalizado com peso 11 independentemente do valor, incluindo diferenças de 0, 1 ou 2 (aceitáveis).

**Correção em `src/timetable/cp_sat_baseline.py`:**
- Criada variável booleana `penaliza_s09`
- `model.Add(diff_var > 2).OnlyEnforceIf(penaliza_s09)` — ativa apenas quando diff > 2
- `model.Add(diff_var <= 2).OnlyEnforceIf(penaliza_s09.Not())` — desativa caso contrário
- Penaliza apenas `penaliza_s09` com peso 11

## Corrigido — F-005 (MAJOR): CP-SAT S10 penaliza qualquer concentração

**Problema:** `var_dia_count` (número de aulas de um professor num dia) era penalizado com peso 10 independentemente do valor.

**Correção em `src/timetable/cp_sat_baseline.py`:**
- Criada variável booleana `penaliza_s10`
- `model.Add(var_dia_count >= 5).OnlyEnforceIf(penaliza_s10)` — ativa apenas quando >= 5 aulas no dia
- `model.Add(var_dia_count <= 4).OnlyEnforceIf(penaliza_s10.Not())` — desativa caso contrário
- Penaliza apenas `penaliza_s10` com peso 10

## Testes adicionados (3 novos)
- `test_cp_sat_s09_diferenca_pequena_nao_penaliza`: verifica que S09 não penaliza quando diferença <= 2
- `test_cp_sat_s10_menos_de_5_aulas_por_dia_nao_penaliza`: verifica que S10 não penaliza quando < 5 aulas/dia
- `test_cp_sat_resolve_instancia_multiplos_professores`: verifica que CP-SAT resolve instância maior sem violações duras

## Cobertura
- `cp_sat_baseline.py`: 90% (mantido)
- Total do projeto: 91.52%

## Escore epistémico
Alta confiança: o uso de `OnlyEnforceIf` no OR-Tools CP-SAT é a abordagem padrão para condicionar penalidades.

## Próximos passos
- T016: Avaliação incremental (F-006, MAJOR)
- T017: Findings MINOR (F-007 a F-011)
