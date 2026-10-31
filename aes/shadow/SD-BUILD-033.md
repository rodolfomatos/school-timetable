# Shadow Doc SD-BUILD-032 — T057 Fase 7: SolverResult e jobs persistentes

## Proveniência
Fase 7 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Introduzir um contrato explícito de resultado e um ciclo de vida durável para execuções do solver.

## Decisões tomadas
- Definir estados: QUEUED, RUNNING, FEASIBLE, OPTIMAL, INFEASIBLE, TIMEOUT, FAILED, CANCELLED, SOLVER_UNAVAILABLE.
- Distinguir estado do job e estado matemático do solver.
- Resultado inclui solution opcional, breakdown de objectivo, hard violations, elapsed time, algorithm/version, parâmetros, seed, best bound/gap quando aplicável, logs e validation report.
- Persistir jobs e resultados; não depender exclusivamente de _solver_tasks em memória.
- Suportar cancelamento e recuperação após reinício.
- Não devolver schedule_version_id=None como conclusão funcional.
- Persistir ScheduleVersion e ScheduleAssignment numa transacção apenas depois de validação independente.
- Garantir idempotência da submissão quando aplicável.

## Escore epistémico
Alta confiança — baseada na arquitetura de sistemas distribuídos e na análise do código existente.

## Próximos passos
- T058: Multi-tenancy, migrações e produção
