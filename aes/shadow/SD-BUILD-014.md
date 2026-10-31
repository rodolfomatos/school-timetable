# Shadow Doc SD-BUILD-014 — Fase 2: Integridade do Modelo CP-SAT (T038)

## Proveniência
Fase 2 do plano de auditoria (DOCX seção 11), iniciada em 31/10/2026.

## Objetivo
Corrigir F-101 (variáveis sobrescritas sem lesson_session_id), F-102 (qualificações docentes), F-103 (S03, S04, S06, S07 no CP-SAT) e alinhar S02, S05, S08, S09, S10 entre Python e CP-SAT.

## Decisões tomadas
- Adicionar lesson_session_id como identidade única para cada sessão requerida
- Implementar TeacherQualification para restringir quais professores podem lecionar cada disciplina
- Implementar S03, S04, S06, S07 no CP-SAT
- Alinhar S02, S05, S08, S09, S10 entre Python e CP-SAT
- Criar testes de equivalência entre CP-SAT e validador Python

## Escore epistémico
Alta confiança — baseada na matriz de rastreabilidade (SD-BUILD-012).

## Próximos passos
- Implementar correções em cp_sat_baseline.py
- Criar testes de equivalência CP-SAT vs validador Python
- Atualizar kanban e métricas
