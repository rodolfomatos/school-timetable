# Shadow Doc SD-BUILD-013 — Fase 1: Auditoria de Restrições (T037)

## Proveniência
Fase 1 do plano de auditoria (DOCX seção 11), concluída em 31/10/2026.

## O que foi construído
- docs/audit/constraint-matrix.md com matriz completa de rastreabilidade de todas as 18 restrições (8 duras + 10 moles)

## Decisões tomadas
- Cada restrição mapeada para: definição formal, âmbito, implementação Python, implementação CP-SAT, peso/penalização, testes, estado e discrepâncias
- 14 findings identificados (F-101 a F-020) com severidade e localização
- F-101 (BLOCKER): CP-SAT usa chave sem lesson_session_id — variáveis sobrescritas
- F-102 (BLOCKER): CP-SAT permite qualquer professor lecionar qualquer disciplina
- F-103 (MAJOR): CP-SAT não implementa S03, S04, S06, S07

## Escore epistémico
Alta confiança — baseado em leitura direta do código Python e CP-SAT, comparado com o DOCX de auditoria.

## Próximos passos
- T038: Corrigir integridade do modelo CP-SAT (lesson_session_id, qualificações docentes, S03-S04-S06-S07)
- T039: Substituir seed esqueleto por construtor de soluções iniciais baseado em dados reais
- T040: Implementar contrato SolverResult
