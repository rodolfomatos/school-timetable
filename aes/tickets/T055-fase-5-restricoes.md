# Ticket T055 — Fase 5: Consistência das restrições S01–S10

## Contexto
CP-SAT e Python usavam fórmulas diferentes para S02, S05, S08, S09, S10; S03/S06
penalizavam excessivamente; S07 usava domínio que impedia violação em vez de
penalizar; S04 criava variáveis duplicadas por slot. Parte do alinhamento foi
feita em T053.

## Objetivo
Definir formalmente S01–S10 e garantir que o avaliador Python e CP-SAT
implementam a mesma semântica, com testes de fronteira e contra-exemplos.

## Causa-raiz (confirmada)
1. **S02 (F-008)**: Python `hora >= 13` vs CP-SAT `eh_manha()` — corrigido em T053.
2. **S05 (F-009)**: Python A-B-A (3 posições), CP-SAT ausente — corrigido em T053
   para A-B-C-A (4 posições) em ambos.
3. **S08 (F-010)**: Python dias totais ≥ 5, CP-SAT 5 consecutivos — corrigido em T053.
4. **S09 (F-011)**: Python diff absoluto > 2, CP-SAT normalizado 25% — corrigido em T053.
5. **S10 (F-012)**: Python `≤2 dias E ≥5 aulas`, CP-SAT `≥5 aulas num dia` — corrigido em T053.
6. **S03/S04/S06/S07**: Já implementados em CP-SAT desde T038, mas sem testes
   de fronteira formais.

## Correções aplicadas
- **docs/spec/soft_constraints_spec.md**: Especificação formal de S01–S10 com
  fórmulas, pesos, limites e requisitos de teste.
- **tests/test_t055_soft_constraints.py**: 36 testes cobrindo:
  - Caso base (penaliza quando deve)
  - Fronteira (não penaliza no limite, ex: hora 12/13, carga=1, diff=2)
  - Contra-exemplo (não penaliza quando não deve, ex: A-B-A vs A-B-C-A)
  - Alinhamento CP-SAT vs Python (smoke test com ortools)
- Testes de S01–S10 todos passando.

## Critérios de Aceitação
- [x] Todas as regras têm especificação formal aprovada.
- [x] Testes unitários cobrem fronteiras e contra-exemplos.
- [x] CP-SAT e Python concordam sobre a penalização (T053 + T055).
- [x] Reificações são bidireccionais quando necessário (S05, S08, S10).
- [x] Matriz de restrições reflecte o estado real (atualizada em T053).
- [x] Nenhuma regra soft é acidentalmente transformada em hard.

## Evidência
- `docs/spec/soft_constraints_spec.md`: 10 regras × fórmula + pesos + limites.
- `tests/test_t055_soft_constraints.py`: 36 testes (4 por regra em média).
- Suite completa: 89.71% cobertura.
- Backend: 9 passed, import OK, lint OK.

## Estado epistémico
- Implementado: **SIM**
- Testado: **SIM**
- Verificado: **SIM**
- Independentemente verificado: **PENDENTE** (T059)

## Fase actual
Plan → Build → Verify → Review (concluído) → Learn.