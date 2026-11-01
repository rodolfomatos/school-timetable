# Ticket T053 — Fase 4: Correção matemática do CP-SAT

## Contexto
O modelo CP-SAT tinha desalinhamentos com o validador Python independente:
- S02 usava `eh_manha()` vs Python `hora >= 13`
- S05 não implementado no CP-SAT (Python tinha A-B-A)
- S08 contava dias consecutivos vs Python dias totais
- S09 normalizava por carga média vs Python diferença absoluta
- S10 usava ≥5 aulas num dia vs Python ≤2 dias e ≥5 aulas

## Objetivo
Alinhar o modelo CP-SAT ao validador Python para que ambas as avaliações sejam consistentes.

## Causa-raiz (confirmada)
1. **S02 (F-008)**: CP-SAT usava `Slot.eh_manha()` (considera `hora_inicio`), Python usava `hora >= 13`.
2. **S05 (F-009)**: CP-SAT tinha apenas `pass`; Python detectava A-B-A (3 posições) mas a especificação pede A-B-C-A (4 posições).
3. **S08 (F-010)**: CP-SAT penalizava 5 dias *consecutivos*; Python penalizava ≥5 dias *totais* com aula.
4. **S09 (F-011)**: CP-SAT normalizava por carga média (25%); Python usava diferença absoluta > 2.
5. **S10 (F-012)**: CP-SAT penalizava ≥5 aulas num único dia; Python penalizava se ≤2 dias e ≥5 aulas.

## Correções aplicadas
- **S02**: CP-SAT alinhado a `sl.hora >= 13` (mesmo que Python).
- **S05**: 
  - Python: alterado para A-B-C-A (4 slots consecutivos, 4 disciplinas distintas).
  - CP-SAT: implementado verificação completa via variáveis booleanas por slot.
- **S08**: CP-SAT alterado para contar dias totais com aula ≥ 5 (mesmo que Python).
- **S09**: CP-SAT alterado para `diff_var > 2` absoluto (mesmo que Python).
- **S10**: CP-SAT alterado para `(dias_com_aula <= 2) AND (total_aulas >= 5)` (mesmo que Python).

## Critérios de Aceitação
- [x] Carga semanal N produz exactamente N sessões distintas (já era).
- [x] Docente/sala não elegível nunca é seleccionado (já era).
- [x] S02 alinhado: tarde = hora ≥ 13.
- [x] S05 implementado no CP-SAT (A-B-C-A).
- [x] S08 alinhado: dias totais ≥ 5.
- [x] S09 alinhado: diferença absoluta > 2.
- [x] S10 alinhado: ≤ 2 dias E ≥ 5 aulas.
- [x] Toda solução CP-SAT passa no validador independente.
- [x] Testes cobrem S02, S05, S08, S09, S10 alinhados.

## Evidência de regressão
- **S05**: Teste antigo (A-B-A) passa no código antigo; teste novo (A-B-C-A) passa no código novo.
- Suite completa: 88.31% cobertura.
- Backend: 9 passed, import OK, lint OK.

## Estado epistémico
- Implementado: **SIM**
- Testado: **SIM**
- Verificado: **SIM**
- Independentemente verificado: **PENDENTE** (T059)

## Fase actual
Plan → Build → Verify → Review (concluído) → Learn.