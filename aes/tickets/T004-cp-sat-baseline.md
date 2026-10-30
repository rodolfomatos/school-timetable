# Ticket T004 — Linha de base exata (CP-SAT / OR-Tools)

## Contexto
O problema de horário escolar é NP-hard. Para validar viabilidade e gerar um seed inicial em instâncias pequenas, é necessária uma linha de base exata. O OR-Tools CP-SAT da Google é o solver exato de referência para este domínio.

## Objetivo
Implementar um `CPSATSolver` completo que:
- Modele o problema como um modelo de programação por restrições (CP-SAT)
- Crie variáveis booleanas para cada (aula, slot, sala) possível
- Adicione restrições duras (H01-H08) como constraints do CP-SAT
- Adicione restrições moles como penalidades no objetivo (adiitivo)
- Resolva dentro de um tempo limite e retorne um `Horario`
- Se `ortools` não estiver instalado, devolva o horário inicial inalterado (fallback)

## Critérios de Aceitação
1. `make test` passa (incluindo novos testes de CP-SAT quando `ortools` disponível).
2. `make lint` passa sem erros.
3. O solver respeita todas as restrições duras na solução de saída.
4. O solver minimiza penalidades moles (função objetivo aditiva).
5. Fallback graceful quando `ortools` não está instalado.

## Riscos (Hostile Analysis)
- Dependência externa (`ortools`) pode não estar disponível em todos os ambientes → mitigação: fallback graceful.
- CP-SAT pode ser lento para instâncias grandes → mitigação: tempo limite configurável.
- Modelação incorreta das restrições duras pode produzir soluções inviáveis → mitigação: testes de validação com `verificar_hard`.

## Estado
**Concluído** (Plan → Build → Verify)

## Critérios de Aceitação — Status
1. `make test` passa (32 testes, incluindo CP-SAT com ortools instalado). — **OK**
2. `make lint` passa sem erros. — **OK**
3. O solver respeita todas as restrições duras na solução de saída. — **OK** (testes de não-duplicação de professor/sala/turma no mesmo slot)
4. O solver minimiza penalidades moles (função objetivo aditiva). — **OK** (modelação com `model.Minimize`)
5. Fallback graceful quando `ortools` não está instalado. — **OK** (teste de fallback)

## Fase atual
Concluído. Próximo: T005 (Metaheurística principal).
