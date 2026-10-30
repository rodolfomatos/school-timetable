# AES Plan Spec — T025 Fluxo de Contestações

## 1. Sumário Executivo
Fluxo central da plataforma: docentes identificam indisponibilidades e contestam slots; administradores gerem contestações e reexecutam o solver.

## 2. Endpoints Backend
- `POST /unavailability` (docente) → marca slot como indisponível com justificação
- `GET /unavailability` (docente/admin) → lista indisponibilidades
- `POST /disputes` (docente) → submete contestação de um slot atribuído
- `GET /disputes` (admin) → lista contestações pendentes
- `PATCH /disputes/{id}` (admin) → aceita/rejeita contestação
- `POST /solver/run-with-constraints` → executa solver com restrições adicionais (indisponibilidades + contestações aceites)

## 3. Fluxo de Trabalho
1. Docente acede ao calendário → clica em slot → seleciona justificação (deslocamento, folga, almoço, compromisso, doença, outro) → guarda
2. Admin gera horário inicial → solver respeita indisponibilidades
3. Docente visualiza horário → clica em aula → submete contestação (motivo + justificação)
4. Admin vê contestação pendente → aceita ou rejeita
5. Se aceita: novo `Unavailability` é criado automaticamente + solver reexecutado → horário atualizado (nova versão)
6. Docente recebe notificação (simulada) do resultado

## 4. Regras de Negócio
- Uma contestação só pode ser submetida pelo docente atribuído à aula
- Uma contestação só pode ser aceita/rejeitada por admin
- Aceitar uma contestação cria automaticamente uma indisponibilidade para esse docente nesse slot
- Após aceitar, o solver deve ser reexecutado (assíncrono) antes de publicar o novo horário
- Histórico de versões do horário é mantido (rascunho → publicado → arquivado)

## 5. Testes E2E (Playwright)
- Docente marca indisponibilidade no calendário
- Admin gera horário respeitando indisponibilidades
- Docente contesta um slot
- Admin aceita contestação → solver reexecuta → horário atualizado
- Admin rejeita contestação → docente vê rejeição

## 6. Frontend Componentes
- `AvailabilityCalendar` — calendário semanal com clique em slot
- `DisputeSubmissionModal` — formulário de contestação
- `DisputeList` — lista de contestações com estado
- `DisputeActionButtons` — aceitar/rejeitar (apenas admin)

## 7. Quality Gates
- Testes E2E Playwright passam
- Testes de unidade backend para endpoints de contestações passam
- Revisão de código aprovada
