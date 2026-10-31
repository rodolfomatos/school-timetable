# Ticket T038 — Fase 2: Integridade do Modelo CP-SAT — CONCLUÍDO

## Estado
**Concluído** (Plan → Build → Verify)

## Correções implementadas

### F-101 (BLOCKER): lesson_session_id como identidade única
- Cada sessão requerida recebe um `lesson_id` único: `f"{turma_id}_{disc_id}_{session_index}"`
- Variáveis CP-SAT indexadas por `lesson_id` em vez de `(turma_id, disc_id)`
- Restrição de cobertura: `Σ(p,r,s) x[lesson_id, p, r, s] = 1` para cada sessão
- Não há sobrescrita de variáveis em dicionário

### F-102 (BLOCKER): Qualificações docentes
- Adicionado campo `qualificacoes: frozenset[str]` ao modelo Professor
- CP-SAT só cria variáveis para combinações (professor, disciplina) onde o professor está qualificado
- Se não há qualificações definidas, assume compatibilidade total (retrocompatibilidade)

### F-103 (MAJOR): Restrições moles faltantes no CP-SAT
- S03 (duas horas consecutivas): Implementado com variáveis booleanas por par de slots consecutivos
- S04 (disciplinas não espalhadas): Implementado com variável booleana "somente um dia"
- S06 (duas horas para avaliação): Implementado para professores com carga >= 4
- S07 (carga fora dos limites): Implementado com variáveis abaixo/acima dos limites
- S08: Penaliza sequências de 5+ dias consecutivos
- S09: Normalizado por carga contratual (máximo 25% de diferença)
- S10: Alinhado com Python (≥ 5 aulas em um único dia)

### Correções adicionais
- S02: Usa `hora_inicio` do Slot quando disponível, senão usa `hora < 13`
- S05: Documentado como pendente (requer modelagem de variáveis por posição de slot)
- S08: Alinhado entre Python e CP-SAT (sequências de 5 dias)

## Testes
- 11 testes CP-SAT passando
- Cobertura do cp_sat_baseline.py: 93%

## Fase Atual
Concluído. Próximo: T039 (Fase 3 - Seed e Validador Independente).
