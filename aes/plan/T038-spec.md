# AES Plan Spec — T038 Fase 2: Integridade do Modelo CP-SAT

## 1. Sumário Executivo
Corrigir problemas críticos no modelo CP-SAT: variáveis sobrescritas sem lesson_session_id, falta de qualificações docentes, restrições moles faltantes (S03, S04, S06, S07) e discrepâncias com o validador Python.

## 2. Mudanças no CP-SAT
### 2.1 Identidade de sessão (F-101)
- Substituir aulas_requeridas: list[tuple[str, str]] por lista de objetos com lesson_session_id único
- Cada sessão requerida recebe um ID único: f"{turma_id}_{disc_id}_{session_index}"
- Variáveis indexadas por lesson_session_id em vez de (turma_id, disc_id)
- Restrição de cobertura: Σ(p,r,s) x[lesson_session_id, p, r, s] = 1 para cada sessão

### 2.2 Qualificações docentes (F-102)
- Adicionar campo qualificacoes ao Professor: list[str] com códigos de disciplina
- Criar variáveis apenas para combinações (professor, disciplina) onde o professor é qualificado
- Validar que disciplinas têm pelo menos um professor qualificado

### 2.3 Restrições moles faltantes (F-103)
- Implementar S03: duas horas consecutivas da mesma disciplina para a mesma turma
- Implementar S04: disciplinas não espalhadas pela semana
- Implementar S06: duas horas consecutivas para avaliação
- Implementar S07: carga horária fora dos limites

### 2.4 Alinhamento S02, S05, S08, S09, S10
- S02: usar hora de início/fim do TimeSlot em vez de número da hora >= 13
- S05: implementar padrão A-B-C-A (4 posições) em vez de A-B-A (3 posições)
- S08: calcular sequências consecutivas em vez de contar dias totais
- S09: normalizar por carga contratual em vez de contagens absolutas
- S10: alinhar condição (≥ 5 aulas em ≤ 2 dias Python vs ≥ 5 aulas em 1 dia CP-SAT)

## 3. Testes
- Teste: cada sessão requerida tem lesson_session_id único
- Teste: carga semanal N resulta em exatamente N sessões distintas
- Teste: professores não qualificados não recebem aulas
- Teste: salas incompatíveis não são selecionadas
- Teste de equivalência: solução CP-SAT passa no validador Python

## 4. Critérios de Aceitação
1. Cada sessão tem lesson_session_id estável e único
2. Restrição de cobertura: soma das variáveis por sessão = 1
3. Variáveis criadas apenas para combinações admissíveis
4. CP-SAT e validador Python são equivalentes para S01-S10, H01-H08
5. Testes de carga semanal 1, 2, 3 e N passam

## Fase atual
Plan → Build.
