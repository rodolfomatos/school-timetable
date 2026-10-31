# Shadow Doc SD-BUILD-025 — T049 Fase 2: Integridade do modelo SQLAlchemy

## Proveniência
Fase 2 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Corrigir e validar integralmente o grafo de entidades e relações SQLAlchemy.

## Decisões tomadas
- Rever Course, Room, Subject, Class, Teacher, User, Unavailability, Dispute, ScheduleVersion e ScheduleAssignment.
- Para cada relationship(back_populates=...), garantir propriedade correspondente e simétrica.
- Garantir que o lado relacional aponta para a entidade certa.
- Garantir ForeignKeys e cardinalidades coerentes.
- Separar perfil de autenticação User do perfil operacional Teacher, com relação 1:0/1 explícita.

## Escore epistémico
Alta confiança — baseada na análise de modelos SQLAlchemy e relacionamentos.

## Próximos passos
- T050: Autenticação e privilégios
