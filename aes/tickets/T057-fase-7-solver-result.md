# Ticket T057 — Fase 7: SolverResult e jobs persistentes

## Contexto
O resultado do solver não é guardado; tarefas existem apenas em memória (_solver_tasks dict); não há persistência de ScheduleVersion/ScheduleAssignment.

## Objetivo
Introduzir um contrato explícito de resultado e um ciclo de vida durável para execuções do solver.

## Critérios de Aceitação
[ ] Job sobrevive a reinício do processo.
[ ] Estados são consultáveis por utilizador autorizado.
[ ] Timeout com incumbent válido é distinguido de timeout sem solução.
[ ] Falha não devolve horário inicial como resultado calculado.
[ ] Solução persistida passa no validador independente.
[ ] Versão e atribuições são consultáveis após nova sessão DB.
[ ] Cancelamento e falha ficam registados.

## Fase atual
Plan → Build → Verify.
