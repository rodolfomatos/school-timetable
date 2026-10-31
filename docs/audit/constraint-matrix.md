# Matriz de Rastreabilidade de Restrições — school-timetable

**Data:** 31 de outubro de 2026  
**Fase:** Fase 1 — Auditoria de Restrições (T037)  
**Referência:** docs/constraints.md, src/timetable/constraints.py, src/timetable/cp_sat_baseline.py, docs/school-timetable-auditoria-plano-refactoring.docx

---

## Legenda

| Coluna | Significado |
|--------|-------------|
| **ID** | Identificador da restrição (Hxx = dura, Sxx = mole) |
| **Definição Formal** | Descrição do que a restrição deve garantir |
| **Âmbito** | A que entidades se aplica |
| **Implementação Python** | Onde está no código `constraints.py` |
| **Implementação CP-SAT** | Onde está no código `cp_sat_baseline.py` |
| **Peso/Penalidade** | Valor da penalidade para restrições moles |
| **Testes** | Testes de unidade associados |
| **Estado** | Implementado / Parcial / Não implementado |
| **Discrepâncias** | Diferenças entre especificação, Python e CP-SAT |

---

## Restrições Duras (Hard)

### H01 — Professor não dá duas aulas no mesmo slot

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ professor p, ∀ slot s: Σ(x[p,*,s,*]) ≤ 1 |
| **Âmbito** | Professor × Slot |
| **Implementação Python** | `verificar_hard()` linhas 58-65 — conta ocorrências de (professor, slot) e flagga se > 1 |
| **Implementação CP-SAT** | Linhas 113-123 — restrição linear `≤ 1` por (professor, slot) |
| **Peso/Penalidade** | N/A (hard) |
| **Testes** | `test_h01_professor_duplicado` em test_constraints.py |
| **Estado** | ✅ Implementado em ambos |
| **Discrepâncias** | Nenhuma |

### H02 — Sala não alberga duas aulas no mesmo slot

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ sala s, ∀ slot t: Σ(x[*,*,s,t]) ≤ 1 |
| **Âmbito** | Sala × Slot |
| **Implementação Python** | `verificar_hard()` linhas 67-74 — conta ocorrências de (sala, slot) |
| **Implementação CP-SAT** | Linhas 125-135 — restrição linear `≤ 1` por (sala, slot) |
| **Peso/Penalidade** | N/A (hard) |
| **Testes** | `test_h02_sala_duplicada` em test_constraints.py |
| **Estado** | ✅ Implementado em ambos |
| **Discrepâncias** | Nenhuma |

### H03 — Turma não tem duas aulas no mesmo slot

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ turma t, ∀ slot s: Σ(x[t,*,*,s]) ≤ 1 |
| **Âmbito** | Turma × Slot |
| **Implementação Python** | `verificar_hard()` linhas 76-83 — conta ocorrências de (turma, slot) |
| **Implementação CP-SAT** | Linhas 137-147 — restrição linear `≤ 1` por (turma, slot) |
| **Peso/Penalidade** | N/A (hard) |
| **Testes** | `test_h03_turma_duplicada` em test_constraints.py |
| **Estado** | ✅ Implementado em ambos |
| **Discrepâncias** | Nenhuma |

### H04 — Sala compatível com a disciplina

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ aula a: sala(a).tipo == disciplina(a).tipo_sala_requerida |
| **Âmbito** | Sala × Disciplina |
| **Implementação Python** | `verificar_hard()` linhas 85-93 — verifica sala.tipo == disc.tipo_sala_requerida |
| **Implementação CP-SAT** | Linhas 149-154 — `model.Add(v == 0)` se tipos diferem |
| **Peso/Penalidade** | N/A (hard) |
| **Testes** | Não há teste específico isolado para H04 |
| **Estado** | ✅ Implementado em ambos |
| **Discrepâncias** | Nenhuma |

### H05 — Professor disponível nesse slot

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ aula a: prof(a).disponibilidade contém slot(a) OU prof(a).disponibilidade está vazia |
| **Âmbito** | Professor × Slot |
| **Implementação Python** | `verificar_hard()` linhas 95-99 — chama `prof.esta_disponivel(slot)` |
| **Implementação CP-SAT** | Linhas 156-160 — `model.Add(v == 0)` se professor não disponível |
| **Peso/Penalidade** | N/A (hard) |
| **Testes** | Não há teste específico isolado para H05 |
| **Estado** | ✅ Implementado em ambos |
| **Discrepâncias** | **F-013 (P0):** `prof.esta_disponivel()` retorna `True` quando `disponibilidade` está vazia. Isso significa que ausência de dados é interpretada como disponibilidade total, o que pode ser incorreto. O DOCX recomenda três estados: UNSPECIFIED, AVAILABLE, UNAVAILABLE. |

### H06 — Tempo de deslocamento entre instituições

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ professor p com commute_time > 0: se aula(p, slot_i) e aula(p, slot_j) em instituições diferentes, então tempo(slot_j) - tempo(slot_i) ≥ commute_time |
| **Âmbito** | Professor × Slot × Instituição |
| **Implementação Python** | **Não implementado** |
| **Implementação CP-SAT** | **Não implementado** |
| **Peso/Penalidade** | N/A (hard) |
| **Testes** | Nenhum |
| **Estado** | ❌ Não implementado |
| **Discrepâncias** | **F-014 (P2):** O modelo não tem conceito de instituição/edifício nem tempo de transição entre slots. Necessário adicionar localização a salas e tempo mínimo de transição. |

### H07 — Professores casados não na mesma turma

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ par casados (p1, p2), ∀ turma t, ∀ slot s: não (aula(p1,t,s) E aula(p2,t,s)) |
| **Âmbito** | Professor × Professor × Turma × Slot |
| **Implementação Python** | `verificar_hard()` linhas 101-115 — verifica pares casados na mesma turma/slot |
| **Implementação CP-SAT** | Linhas 162-179 — `OnlyEnforceIf(v)` para bloquear cônjuge na mesma turma/slot |
| **Peso/Penalidade** | N/A (hard) |
| **Testes** | `test_h07_casados_mesma_turma` em test_constraints.py |
| **Estado** | ✅ Implementado em ambos |
| **Discrepâncias** | **F-014 (P0):** O DOCX levanta preocupação de privacidade e discriminação. Recomenda que relações pessoais sejam tratadas como incompatibilidades específicas, justificadas e controladas, não como regras genéricas. |

### H08 — Filho não na turma dos pais casados

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ rel(filho), ∀ professor pai/mãe p: não (aula(p, turma_filho, *)) |
| **Âmbito** | Professor × Turma |
| **Implementação Python** | `verificar_hard()` linhas 117-125 — verifica se professor pai/mãe leciona na turma do filho |
| **Implementação CP-SAT** | Linhas 181-188 — `model.Add(v == 0)` se professor é pai/mãe e turma é do filho |
| **Peso/Penalidade** | N/A (hard) |
| **Testes** | `test_h08_filho_na_turma_dos_pais` em test_constraints.py |
| **Estado** | ✅ Implementado em ambos |
| **Discrepâncias** | **F-014 (P0):** Mesma preocupação que H07 — relações familiares como regras genéricas de distribuição de horários podem introduzir discriminação. |

---

## Restrições Moles (Soft)

### S01 — Dia de folga preferido do professor

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ professor p com dia_folga_preferido d: minimizar contagem de aulas de p em d |
| **Âmbito** | Professor × Dia |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 135-148 — penaliza se aula no dia de folga |
| **Implementação CP-SAT** | Linhas 191-196 — penaliza variável booleana se slot.dia == dia_folga_preferido |
| **Peso/Penalidade** | 10 em ambos |
| **Testes** | Não há teste específico isolado para S01 |
| **Estado** | ✅ Implementado em ambos |
| **Discrepâncias** | Nenhuma |

### S02 — Preferência manhã/tarde do professor

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ professor p com prefere_manha=True: minimizar aulas de p em slots com hora ≥ 13 |
| **Âmbito** | Professor × Slot |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 150-160 — penaliza se `aula.slot.hora >= 13` |
| **Implementação CP-SAT** | Linhas 198-200 — penaliza se `sl.hora >= 13` |
| **Peso/Penalidade** | 8 em ambos |
| **Testes** | Não há teste específico isolado para S02 |
| **Estado** | ⚠️ Implementado com limitação |
| **Discrepâncias** | **F-008 (P1):** O limite é baseado no número da hora (hora ≥ 13) sem considerar o horário real de início/fim das aulas. O modelo Slot não tem hora de início/fim, apenas número inteiro. |

### S03 — Duas horas consecutivas da mesma disciplina para a mesma turma

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ turma t, ∀ disciplina d com carga ≥ 2: existir pelo menos um par de slots (s, s+1) no mesmo dia com aula de d para t |
| **Âmbito** | Turma × Disciplina × Slot |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 162-183 — verifica slots consecutivos ordenados |
| **Implementação CP-SAT** | **Não implementado** |
| **Peso/Penalidade** | 6 |
| **Testes** | Não há teste específico isolado para S03 |
| **Estado** | ⚠️ Implementado apenas em Python |
| **Discrepâncias** | **F-103:** CP-SAT não implementa S03. O validador independente e o solver podem produzir resultados divergentes. |

### S04 — Disciplinas não espalhadas pela semana

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ turma t, ∀ disciplina d: as aulas de d para t não devem estar todas num único dia (se houver ≥ 2 aulas) |
| **Âmbito** | Turma × Disciplina × Dia |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 241-264 — penaliza se todas as aulas de (turma, disciplina) estão num único dia |
| **Implementação CP-SAT** | **Não implementado** |
| **Peso/Penalidade** | 5 |
| **Testes** | Não há teste específico isolado para S04 |
| **Estado** | ⚠️ Implementado apenas em Python |
| **Discrepâncias** | **F-103:** CP-SAT não implementa S04. |

### S05 — Padrão A-B-C-A (mesma disciplina interrompida)

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ turma t, ∀ dia d: não existir sequência de slots s1 < s2 < s3 < s4 tal que disciplina(s1) == disciplina(s3) == D, disciplina(s2) != D, disciplina(s4) == D |
| **Âmbito** | Turma × Dia × Slot |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 266-290 — verifica `disciplinas_ordenadas[i] == disciplinas_ordenadas[i+2] and != disciplinas_ordenadas[i+1]` |
| **Implementação CP-SAT** | **Não implementado** |
| **Peso/Penalidade** | 7 |
| **Testes** | Não há teste específico isolado para S05 |
| **Estado** | ⚠️ Implementado incorretamente em Python |
| **Discrepâncias** | **F-009 (P1):** O código Python verifica `disciplinas_ordenadas[i] == disciplinas_ordenadas[i+2]` (padrão A-B-A de 3 posições), não o padrão A-B-C-A de 4 posições descrito na documentação. **F-103:** CP-SAT não implementa S05. |

### S06 — Falta de duas horas consecutivas para avaliação

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ professor p com carga_maxima ≥ 4: existir pelo menos um bloco de 2h consecutivas em algum dia |
| **Âmbito** | Professor × Dia |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 292-312 — verifica se existem 2 horas consecutivas para professores com carga ≥ 4 |
| **Implementação CP-SAT** | **Não implementado** |
| **Peso/Penalidade** | 9 |
| **Testes** | Não há teste específico isolado para S06 |
| **Estado** | ⚠️ Implementado apenas em Python |
| **Discrepâncias** | **F-103:** CP-SAT não implementa S06. **F-011 (MINOR):** Deve ser aplicado apenas a professores com necessidade real de avaliação, não automaticamente a todos. |

### S07 — Carga horária do professor fora dos limites

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ professor p: carga_minima_semanal ≤ total_aulas(p) ≤ carga_maxima_semanal |
| **Âmbito** | Professor |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 314-331 — penaliza se fora dos limites |
| **Implementação CP-SAT** | **Não implementado** |
| **Peso/Penalidade** | 8 |
| **Testes** | Não há teste específico isolado para S07 |
| **Estado** | ⚠️ Implementado apenas em Python |
| **Discrepâncias** | **F-103:** CP-SAT não implementa S07. |

### S08 — Professor a trabalhar muitos dias seguidos sem pausa

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ professor p: penalizar sequências longas de dias de trabalho consecutivos |
| **Âmbito** | Professor × Dia |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 185-201 — penaliza se `len(dias_com_aula) >= 5` |
| **Implementação CP-SAT** | Linhas 202-224 — conta dias distintos com ≥ 1 aula, penaliza cada dia com variável booleana |
| **Peso/Penalidade** | 12 em ambos |
| **Testes** | Não há teste específico isolado para S08 |
| **Estado** | ⚠️ Implementado em ambos com lógica diferente |
| **Discrepâncias** | **F-010 (P1):** O Python penaliza se o professor leciona em ≥ 5 dias diferentes (contagem total). O CP-SAT penaliza cada dia individualmente com variável booleana. As semânticas diferem: o DOCX recomenda "calcular sequências, dias de descanso e carga diária" em vez de apenas contar dias totais. |

### S09 — Distribuição desigual de aulas entre professores

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ disciplina d: max(contagem(prof)) - min(contagem(prof)) ≤ 2 (ou normalizado por carga contratual) |
| **Âmbito** | Disciplina × Professor |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 203-224 — penaliza se max - min > 2 |
| **Implementação CP-SAT** | Linhas 226-252 — mesma lógica com diff_var > 2 |
| **Peso/Penalidade** | 11 em ambos |
| **Testes** | Não há teste específico isolado para S09 |
| **Estado** | ✅ Implementado em ambos |
| **Discrepâncias** | **F-011 (P1):** O DOCX recomenda normalizar pela carga contratual/atribuída de cada professor, não comparar contagens absolutas. Dois professores com cargas diferentes podem ter distribuição "desigual" em contagem absoluta mas justificada por carga contratual. |

### S10 — Carga concentrada em poucos dias para o mesmo professor

| Campo | Valor |
|-------|-------|
| **Definição Formal** | ∀ professor p: penalizar se ≥ 5 aulas em ≤ 2 dias |
| **Âmbito** | Professor × Dia |
| **Implementação Python** | `calcular_penalidades_moles()` linhas 226-239 — penaliza se `len(dias) <= 2 and len(aulas) >= 5` |
| **Implementação CP-SAT** | Linhas 254-270 — penaliza se `var_dia_count >= 5` em um único dia |
| **Peso/Penalidade** | 10 em ambos |
| **Testes** | Não há teste específico isolado para S10 |
| **Estado** | ⚠️ Implementado em ambos com lógica diferente |
| **Discrepâncias** | **F-012 (MAJOR):** O Python penaliza se o professor tem ≥ 5 aulas distribuídas em ≤ 2 dias. O CP-SAT penaliza se há ≥ 5 aulas em um único dia. São condições diferentes. |

---

## Resumo de Descrepâncias Críticas

| ID | Severidade | Descrição | Local |
|----|-----------|-----------|-------|
| F-101 | BLOCKER | CP-SAT usa chave `(turma, disc, prof, sala, slot)` sem `lesson_session_id` — variáveis sobrescritas quando a mesma combinação aparece múltiplas vezes (carga_semanal > 1) | `cp_sat_baseline.py` linhas 79-83, 92-98 |
| F-102 | BLOCKER | CP-SAT permite que qualquer professor lecione qualquer disciplina (sem qualificações/docências) | `cp_sat_baseline.py` linhas 86-88 |
| F-103 | MAJOR | CP-SAT não implementa S03, S04, S06, S07 — validador independente e solver podem produzir resultados divergentes | `cp_sat_baseline.py` |
| F-008 | P1 | S02 baseado em número da hora (>= 13) sem relógio real | `constraints.py` linha 153, `cp_sat_baseline.py` linha 199 |
| F-009 | P1 | S05 detecta A-B-A (posições i, i+2) em vez de A-B-C-A (4 posições) | `constraints.py` linhas 274-278 |
| F-010 | P1 | S08 conta dias totais em vez de sequências consecutivas | `constraints.py` linha 190, `cp_sat_baseline.py` linhas 204-224 |
| F-011 | P1 | S09 compara contagens absolutas entre docentes sem normalizar por carga contratual | `constraints.py` linha 213, `cp_sat_baseline.py` linha 248 |
| F-012 | MAJOR | S10: Python penaliza ≥ 5 aulas em ≤ 2 dias; CP-SAT penaliza ≥ 5 aulas em 1 dia | `constraints.py` linha 229, `cp_sat_baseline.py` linha 268 |
| F-013 | P0 | H05: lista de disponibilidade vazia significa disponibilidade total (deveria ser tri-state UNSPECIFIED/AVAILABLE/UNAVAILABLE) | `constraints.py` linha 98, `models.py` |
| F-014 | P0 | H07/H08: relações familiares genéricas, risco de privacidade/discriminação | `constraints.py` linhas 101-125, `cp_sat_baseline.py` linhas 162-188 |

---

## Próximos Passos (Fase 2)

A Fase 2 (T038) deve:
1. Corrigir F-101: adicionar `lesson_session_id` como identidade única para cada sessão requerida
2. Corrigir F-102: implementar relação de qualificação docente (TeacherQualification)
3. Corrigir F-103: implementar S03, S04, S06, S07 no CP-SAT
4. Alinhar S02, S05, S08, S09, S10 entre Python e CP-SAT
5. Criar testes de equivalência entre CP-SAT e validador Python
