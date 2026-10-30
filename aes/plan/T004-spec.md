# AES Plan Spec — T004 CP-SAT Baseline

## 1. Sumário Executivo
Implementar solver exato CP-SAT (OR-Tools) como linha de base para o problema de horário escolar. Valida viabilidade e gera seed inicial para instâncias pequenas.

## 2. Modelo CP-SAT
### Variáveis
Para cada aula possível (turma, disciplina, professor, sala, slot), cria-se uma variável booleana `x[turma, disciplina, professor, sala, slot]`.

### Restrições Duras (hard constraints no CP-SAT)
- H01: Para cada (professor, slot), soma de variáveis <= 1
- H02: Para cada (sala, slot), soma de variáveis <= 1
- H03: Para cada (turma, slot), soma de variáveis <= 1
- H04: Se sala.tipo != disciplina.tipo_sala_requerida, variável = 0
- H05: Se professor não disponível no slot, variável = 0
- H07: Para cada (turma, slot) e par de professores casados, soma <= 1
- H08: Se turma é do filho dos pais casados, professor pai/mãe não leciona nessa turma

### Restrições de cobertura
- Cada (turma, disciplina) deve ter exatamente `carga_semanal` aulas atribuídas

### Função Objetivo (moles, aditiva)
- Minimizar soma de penalidades pelas restrições moles (S01-S10)

## 3. Interface
`CPSATSolver.resolver(horario_inicial, ctx, tempo_limite_segundos) -> Horario`

## 4. Fallback
Se `ortools` não estiver instalado, retorna `horario_inicial.clone()`.

## 5. Testes
- Teste de viabilidade com instância pequena
- Teste de restrições duras respeitadas
- Teste de fallback quando ortools não disponível
