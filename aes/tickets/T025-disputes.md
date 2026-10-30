# Ticket T025 — Fluxo de Contestações Docente ↔ Admin

## Contexto
O fluxo central da plataforma: docentes identificam indisponibilidades e contestam slots atribuídos; administradores gerem estas contestações e reexecutam o solver quando necessário.

## Objetivo
Implementar:
- Docente submete indisponibilidade (slot + justificação pré-definida) via calendário
- Docente contesta um slot atribuído no seu horário (motivo livre + justificação pré-definida)
- Admin visualiza lista de contestações pendentes
- Admin aceita ou rejeita contestação
- Ao aceitar, o solver é reexecutado com a nova restrição e o horário é atualizado
- Notificações (simuladas) para docente quando a contestação é resolvida
- Histórico de alterações de horário (versões rascunho/publicado/arquivado)

## Critérios de Aceitação
1. Endpoint `POST /constraints/unavailability` para docente marcar indisponibilidade
2. Endpoint `POST /disputes` para docente submeter contestação
3. Endpoint `GET /disputes` para admin listar pendentes
4. Endpoint `PATCH /disputes/{id}` para admin aceitar/rejeitar
5. Endpoint `POST /solver/run-with-constraints` que aceita restrições adicionais
6. Frontend com calendário de indisponibilidades (clicar em slot → escolher justificação)
7. Frontend com portal de contestações (ver, submeter, acompanhar estado)
8. Testes E2E com Playwright para o fluxo completo
9. Nenhuma contestação pode ser aceita sem reexecutar o solver

## Riscos (Hostile Analysis)
- Contestação duplicada (mesmo slot, mesmo docente) → mitigação: validação única no backend
- Reexecutar solver a cada contestação é lento → mitigação: fila de processamento assíncrono, notificação quando pronto
- Docente contesta slot de outro docente → mitigação: verificação de propriedade no backend
- Admin aceita contestação que cria conflito → mitigação: solver valida restrições duras antes de publicar

## Fase atual
Plan → Build.
