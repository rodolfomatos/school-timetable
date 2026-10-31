# Shadow Doc SD-BUILD-012 — Fase 1: Auditoria de Restrições (T037)

## Proveniência
Fase 1 do plano de auditoria (DOCX seção 11), iniciada em 31/10/2026.

## Objetivo
Produzir docs/audit/constraint-matrix.md com rastreabilidade completa de todas as restrições duras e moles, identificando discrepâncias entre especificação, código Python e CP-SAT.

## Decisões tomadas
- Extrair restrições de docs/constraints.md, código Python (constraints.py, cp_sat_baseline.py) e DOCX de auditoria
- Matriz de rastreabilidade com: ID, definição formal, âmbito, implementação Python, implementação CP-SAT, peso/penalização, testes, estado e discrepâncias
- Verificar especificamente H01-H08 e S01-S10
- Verificar suspeitas S02, S05, S08, S09, S10
- Verificar H07/H08 (relações familiares)

## Escore epistémico
Alta confiança — baseado em revisão direta do código e do DOCX de auditoria.

## Próximos passos
- Criar docs/audit/constraint-matrix.md
- Identificar discrepâncias entre CP-SAT e validador Python
- Relatório de findings em docs/audit/findings.md
