# Especificação Formal das Restrições Moles S01–S10

## Convenções
- `H` = conjunto de aulas no horário
- `A` = aula individual
- `A.turma`, `A.disciplina`, `A.professor`, `A.sala`, `A.slot`, `A.subgrupo_id`
- `S` = slot (`dia`, `hora`)
- `P` = professor
- `D` = disciplina
- `T` = turma
- `C` = contexto (`ContextoRestricoes`)

---

## S01 — Dia de folga preferido

**Definição**: Penalizar cada aula que ocorra no dia de folga preferido do professor.

**Fórmula**:  
`penalty = 10 × |{ a ∈ H : a.professor.dia_folga_preferido ≠ ∅ ∧ a.slot.dia = a.professor.dia_folga_preferido }|`

**Variáveis**: `dia_folga_preferido` opcional por professor.

**CP-SAT**: Variável booleana por aula, peso 10.

**Limite**: Apenas se `dia_folga_preferido` definido.

---

## S02 — Preferência manhã/tarde

**Definição**: Penalizar aulas à tarde para professores que preferem manhã.

**Fórmula**:  
`penalty = 8 × |{ a ∈ H : a.professor.prefere_manha = True ∧ a.slot.hora ≥ 13 }|`

**Nota**: Usa `slot.hora` absoluta (não `hora_inicio`), alinhado entre Python e CP-SAT.

**CP-SAT**: Variável booleana por aula, peso 8.

---

## S03 — Duas horas consecutivas (mesma disciplina, mesma turma)

**Definição**: Para cada par (turma, disciplina), deve existir pelo menos um par de slots consecutivos no mesmo dia com aulas dessa disciplina.

**Fórmula**:  
Para cada `(t, d)` com `carga_semanal(d) ≥ 2`:
```
tem_consecutivo(t,d) = ∃ dia, h : 
    (t,d) tem aula em (dia, h) ∧ (t,d) tem aula em (dia, h+1)

penalty = 6 × |{ (t,d) : carga_semanal(d) ≥ 2 ∧ ¬tem_consecutivo(t,d) }|
```

**Python**: Verifica pares de aulas ordenadas por (dia, hora).

**CP-SAT**: Variáveis auxiliares `var_tem_aula_s1`, `var_tem_aula_s2`, `var_bloco` com `OnlyEnforceIf`.

**Limite**: Apenas se `carga_semanal ≥ 2`.

---

## S04 — Disciplinas espalhadas pela semana

**Definição**: Penalizar se todas as aulas de uma (turma, disciplina) caírem num único dia (e houver ≥ 2 aulas).

**Fórmula**:  
Para cada `(t, d)`:
```
dias_com_aula(t,d) = |{ dia : ∃ h, (t,d) tem aula em (dia, h) }|
total_aulas(t,d) = |{ a ∈ H : a.turma=t ∧ a.disciplina=d }|

penalty = 5 × |{ (t,d) : dias_com_aula(t,d) = 1 ∧ total_aulas(t,d) ≥ 2 }|
```

**Python**: Conta dias únicos com aulas dessa disciplina.

**CP-SAT**: Variável booleana por dia, `var_somente_um_dia` via soma = 1.

**Limite**: Apenas se `total_aulas ≥ 2`.

---

## S05 — Padrão A-B-C-A (mesma disciplina interrompida)

**Definição**: Em slots consecutivos do mesmo dia para a mesma turma, penalizar sequência `D1, D2, D3, D1` onde `D1 ≠ D2 ≠ D3 ≠ D1`.

**Fórmula**:  
Para cada turma `t` e dia `d`, seja `seq = [a.disciplina for a em H se a.turma=t ∧ a.slot.dia=d ordenado por a.slot.hora]`.
```
penalty = 7 × |{ (t,d) : ∃ i, seq[i]=seq[i+3] ∧ seq[i]≠seq[i+1] ∧ seq[i]≠seq[i+2] ∧ seq[i+1]≠seq[i+2] }|
```

**Python**: Loop sobre `disciplinas_ordenadas`, verifica `i` e `i+3`.

**CP-SAT**: Variáveis `var_tem_aula` por (lesson_id, slot), `var_padrao` com `OnlyEnforceIf` para 4 slots consecutivos.

**Limite**: Requer ≥ 4 slots consecutivos no mesmo dia.

---

## S06 — Bloco de 2h para avaliação (professores carga ≥ 4)

**Definição**: Professores com `carga_maxima_semanal ≥ 4` devem ter pelo menos um bloco de 2h consecutivas em cada dia onde lecionam ≥ 2 aulas.

**Fórmula**:  
Para cada professor `p` com `p.carga_maxima_semanal ≥ 4` e dia `d`:
```
horas_p_d = sorted({ a.slot.hora : a ∈ H, a.professor=p, a.slot.dia=d })
tem_bloco(p,d) = ∃ i : horas_p_d[i+1] = horas_p_d[i] + 1

penalty = 9 × |{ (p,d) : p.carga_maxima_semanal ≥ 4 ∧ |horas_p_d| ≥ 2 ∧ ¬tem_bloco(p,d) }|
```

**Python**: Verifica `horas[i]+1 == horas[i+1]`.

**CP-SAT**: Variáveis `var_tem_aula_s1`, `var_tem_aula_s2`, `var_bloco` com `OnlyEnforceIf`.

**Limite**: Apenas para professores com `carga_maxima_semanal ≥ 4` e `|horas| ≥ 2`.

---

## S07 — Carga horária fora dos limites

**Definição**: Penalizar se total de aulas do professor estiver fora de `[carga_minima_semanal, carga_maxima_semanal]`.

**Fórmula**:  
```
total(p) = |{ a ∈ H : a.professor = p }|

penalty = 8 × |{ p : total(p) < p.carga_minima_semanal }|
        + 8 × |{ p : total(p) > p.carga_maxima_semanal }|
```

**Python**: Conta aulas, compara com limites.

**CP-SAT**: Variável inteira `total_aulas_var`, `var_abaixo`, `var_acima` com `OnlyEnforceIf`.

---

## S08 — Professor em 5+ dias diferentes

**Definição**: Penalizar professores que lecionam em 5 ou mais dias diferentes na semana.

**Fórmula**:  
```
dias_com_aula(p) = |{ d : ∃ a ∈ H, a.professor=p, a.slot.dia=d }|

penalty = 12 × |{ p : dias_com_aula(p) ≥ 5 }|
```

**Python**: Conta dias únicos.

**CP-SAT**: Variável booleana por dia, `var_soma_dias ≥ 5` via `var_5_ou_mais`.

**Nota**: Conta dias totais, **não** sequências consecutivas. Alinhado entre Python e CP-SAT desde T053.

---

## S09 — Distribuição desigual entre professores da mesma disciplina

**Definição**: Para cada disciplina com ≥ 2 professores, penalizar se a diferença entre o máximo e mínimo de aulas atribuídas for > 2.

**Fórmula**:  
Para cada disciplina `d` com professores `P_d`:
```
contagens = [ |{ a ∈ H : a.disciplina=d ∧ a.professor=p }| : p ∈ P_d ]
diferença = max(contagens) - min(contagens)

penalty = 11 × |{ d : |P_d| ≥ 2 ∧ diferença > 2 }|
```

**Python**: Diferença absoluta > 2.

**CP-SAT**: `max_var`, `min_var`, `diff_var = max - min`, `diff_var > 2`.

**Nota**: Diferença **absoluta**, não normalizada por carga. Alinhado desde T053.

---

## S10 — Carga concentrada em poucos dias

**Definição**: Penalizar se professor tem ≥ 5 aulas concentradas em ≤ 2 dias.

**Fórmula**:  
Para cada professor `p`:
```
total_aulas(p) = |{ a ∈ H : a.professor=p }|
dias_com_aula(p) = |{ d : ∃ a ∈ H, a.professor=p, a.slot.dia=d }|

penalty = 10 × |{ p : total_aulas(p) ≥ 5 ∧ dias_com_aula(p) ≤ 2 }|
```

**Python**: `total ≥ 5` E `dias ≤ 2`.

**CP-SAT**: `var_total_aulas ≥ 5` E `var_soma_dias ≤ 2` via `var_concentrada` e `var_muitas_aulas`.

**Nota**: Condição **conjunta** (E), não OU. Alinhado desde T053.

---

## Pesos Sumário

| ID  | Peso | Trigger |
|-----|------|---------|
| S01 | 10   | aula no dia de folga |
| S02 | 8    | aula à tarde (prefere manhã) |
| S03 | 6    | sem bloco 2h consecutivas |
| S04 | 5    | todas aulas num só dia |
| S05 | 7    | padrão A-B-C-A |
| S06 | 9    | sem bloco 2h para avaliação (carga≥4) |
| S07 | 8    | carga fora [min, max] |
| S08 | 12   | ≥ 5 dias com aula |
| S09 | 11   | max-min > 2 entre profs da mesma disc |
| S10 | 10   | ≥5 aulas em ≤2 dias |

---

## Requisitos de Teste (T055)

Para cada S01–S10:
- [ ] Teste caso base (penaliza quando deve)
- [ ] Teste fronteira (não penaliza no limite)
- [ ] Teste contra-exemplo (não penaliza quando não deve)
- [ ] Teste CP-SAT vs Python concordam na contagem de penalidades
- [ ] Teste casos edge: carga=1, carga=0, subgrupos, slots imutáveis