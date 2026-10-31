# Ticket T052 — Fase 3: Construção de solução inicial

## Contexto
SA e Tabu Search começam com Horario() vazio e devolvem horário vazio. Seed usa valores hard-coded.

## Objetivo
Substituir placeholders em seed.py por construção baseada no ProblemInstance; não usar nomes fixos; garantir que problemas com sessões obrigatórias não devolvem horário vazio.

## Critérios de Aceitação
[ ] Problema com sessões obrigatórias não pode produzir sucesso com horário vazio.
[ ] Número de sessões atribuídas corresponde ao número requerido, salvo estado parcial explícito.
[ ] Seed passa pelo validador independente.
[ ] Seed é reprodutível para a mesma instância e random seed.
[ ] Seed não contém entidades fora do ProblemInstance.
[ ] SA/Tabu recusam input inviável ou vazio, salvo modo explicitamente permitido.
[ ] Testes cobrem problema viável, inviável e parcialmente preenchível.

## Fase atual
Plan → Build → Verify.
