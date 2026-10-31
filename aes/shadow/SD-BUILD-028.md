# Shadow Doc SD-BUILD-027 — T051 Fase 3: Modelo de domínio e integração

## Proveniência
Fase 3 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Criar uma camada de domínio canónica, independente do ORM, que traduza os dados institucionais num problema de timetabling completo e consistente.

## Decisões tomadas
- Criar DTOs/modelos de entrada do solver independentes de SQLAlchemy.
- Construir contexto a partir de relações reais: turma ↔ curso ↔ disciplina; docente ↔ qualificações ↔ sessões; sala ↔ capacidade/equipamento/disponibilidade.
- Deixar de combinar indiscriminadamente todas as turmas com todas as disciplinas.
- Carregar e aplicar indisponibilidades persistidas e additional_unavailabilities.
- Modelar qualificações docentes de forma explícita.
- Modelar carga lectiva em unidades claras (minutos/horas de contacto e número de sessões).
- Validar dados em falta e inconsistências antes de chamar o solver.
- Definir identificador e versão imutável do problema de optimização.

## Escore epistémico
Alta confiança — baseada na análise de modelagem de domínio e integração solver-banco de dados.

## Próximos passos
- T052: Construção de solução inicial
