# AES Plan Spec — T018 Validação com Dados Reais

## 1. Sumário Executivo
Validar o solver com dados reais de escola média para medir escala, performance e qualidade da solução.

## 2. Dataset Realista
- 10 turmas (anos 7-12, 2 turmas por ano)
- 15 professores (com disponibilidades, dias de folga, preferências manhã/tarde)
- 12 disciplinas (Matemática, Português, Inglês, Ciências, História, Geografia, Física, Química, Biologia, Educação Física, Artes, Informática)
- 8 salas (6 normais, 2 laboratórios)
- 40 slots/semana (segunda-sexta, 8h-16h, 8 períodos)
- Carga semanal por disciplina: 2-5 aulas
- Relacionamentos: 2 casamentos de professores, 1 relação filho

## 3. Testes de Performance
- Executar CP-SAT com tempo limite de 60s
- Executar Simulated Annealing com tempo limite de 60s
- Executar Tabu Search com tempo limite de 60s
- Medir: tempo de execução, score, violações duras, penalidades moles

## 4. Critérios de Sucesso
- Solução viável (sem violações duras) encontrada em ≤ 60s
- Score razoável (menos de 50 penalidades moles)
- Tempo de execução documentado para referência futura
