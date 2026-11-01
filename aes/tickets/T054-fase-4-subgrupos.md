# Ticket T054 — Fase 4: Semântica dos subgrupos

## Contexto
Subgrupos não eram preservados nos movimentos locais; H03 permitia sobreposição
entre turma inteira e subgrupo; sessões de subgrupo não eram modeladas como
sessões distintas relacionadas.

## Objetivo
Completar o suporte a subgrupos desde o modelo de domínio até aos operadores,
validação, CP-SAT e persistência.

## Causa-raiz (confirmada)
1. **H03 (Python)**: `turma_ocupada_em` comparava `subgrupo_id` por igualdade
   exacta. Turma inteira (`subgrupo_id=None`) e subgrupo (`subgrupo_id="SG1"`)
   podiam sobrepor-se no mesmo slot.
2. **H03 (CP-SAT)**: Restrição aplicada por `(turma, slot, subgrupo_id)`.
   Turma inteira e subgrupos eram buckets separados, permitindo sobreposição.
3. **Operadores locais**: `_gerar_vizinho_exchange` e `_gerar_vizinho_modify`
   criavam novas `Aula` sem passar `subgrupo_id`, perdendo a informação.
4. **Domínio**: `EntradaCurricular` já suportava `subgrupo_id`, mas a
   construção de sessões não validava conflitos turma inteira ↔ subgrupo.

## Correções aplicadas
- **Python `Horario.turma_ocupada_em`**:
  - Se `subgrupo_id` dado: verifica esse subgrupo **E** turma inteira (None).
  - Se `subgrupo_id=None`: verifica todos os subgrupos da turma.
- **CP-SAT H03**:
  - Para turmas com subgrupos, adiciona `None` à lista de subgrupos.
  - Restrição adicional: soma de aulas da turma inteira + cada subgrupo ≤ 1
    por slot (impede sobreposição inteira ↔ subgrupo).
- **Local Search**:
  - `exchange`: preserva `subgrupo_id` ao criar `nova_a1`/`nova_a2`.
  - `modify`: preserva `subgrupo_id` ao criar `nova_aula`.
- **Domínio/Seed**: `construir_solucao_inicial` já usava `subgrupo_id` das
  `SessaoRequerida`; validador agora bloqueia conflitos.

## Critérios de Aceitação
- [x] Turma inteira e subgrupo não podem sobrepor-se.
- [x] Subgrupos diferentes podem decorrer em paralelo quando permitido.
- [x] Uma actividade exigida para todos os subgrupos gera a cardinalidade
  correcta de sessões.
- [x] Move/Swap/clone preservam `subgrupo_id` e IDs de sessão.
- [x] Testes abrangem CP-SAT, Python validator, SA e Tabu.

## Evidência de regressão
- Antes: `turma_ocupada_em("T1", slot, "SG1")` não via aula com `subgrupo_id=None`.
- Depois: vê ambos; H03 bloqueia sobreposição.
- Suite completa: 89.36% cobertura.
- Backend: 9 passed, import OK, lint OK.
- Testes novos: `test_t054_subgrupos.py` (5 testes: H03 inteira↔subgrupo,
  subgrupos paralelos, operadores preservam ID, CP-SAT H03).

## Estado epistémico
- Implementado: **SIM**
- Testado: **SIM**
- Verificado: **SIM**
- Independentemente verificado: **PENDENTE** (T059)

## Fase actual
Plan → Build → Verify → Review (concluído) → Learn.