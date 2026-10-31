# AES Plan Spec — T057 Fase 7: SolverResult e jobs persistentes

## 1. Sumário Executivo
Introduzir um contrato explícito de resultado e um ciclo de vida durável para execuções do solver.

## 2. Objetivo
- Definir estados: QUEUED, RUNNING, FEASIBLE, OPTIMAL, INFEASIBLE, TIMEOUT, FAILED, CANCELLED, SOLVER_UNAVAILABLE.
- Distinguir estado do job e estado matemático do solver.
- Resultado inclui solution opcional, breakdown de objectivo, hard violations, elapsed time, algorithm/version, parâmetros, seed, best bound/gap quando aplicável, logs e validation report.
- Persistir jobs e resultados; não depender exclusivamente de _solver_tasks em memória.
- Suportar cancelamento e recuperação após reinício.
- Não devolver schedule_version_id=None como conclusão funcional.
- Persistir ScheduleVersion e ScheduleAssignment numa transacção apenas depois de validação independente.
- Garantir idempotência da submissão quando aplicável.

## 3. Critérios de Aceitação
[ ] Job sobrevive a reinício do processo.
[ ] Estados são consultáveis por utilizador autorizado.
[ ] Timeout com incumbent válido é distinguido de timeout sem solução.
[ ] Falha não devolve horário inicial como resultado calculado.
[ ] Solução persistida passa no validador independente.
[ ] Versão e atribuições são consultáveis após nova sessão DB.
[ ] Cancelamento e falha ficam registados.

## 4. Fase atual
Plan → Build → Verify.
