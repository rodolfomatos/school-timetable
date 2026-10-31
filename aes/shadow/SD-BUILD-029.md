# Shadow Doc SD-BUILD-029 — T053 Fase 4: Correção matemática do CP-SAT

## Proveniência
Fase 4 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Garantir que cada sessão requerida tem identidade única e estável; que cada sessão l tem exatamente uma atribuição admissível; que variáveis são criadas apenas para combinações admissíveis; que restrições duras são modeladas correctamente.

## Decisões tomadas
- Cada sessão recebe um lesson_session_id único e estável.
- Restrição de cobertura: sum(x[l,teacher,room,timeslot,...]) == 1 para cada sessão l.
- Variáveis criadas apenas para docentes qualificados, salas compatíveis e slots temporalmente admissíveis.
- Modelar duração real e sobreposição de intervalos sem permitir sobreposições parciais.
- Impedir conflitos de turma/grupo, docente e sala.
- Distinguir sessões simultâneas de grupos diferentes e aulas partilhadas.
- Garantir que a carga semanal resulta no número correcto de sessões e duração total.

## Escore epistémico
Alta confiança — baseada na literatura de constraint programming e na análise do CP-SAT existente.

## Próximos passos
- T054: Semântica dos subgrupos
