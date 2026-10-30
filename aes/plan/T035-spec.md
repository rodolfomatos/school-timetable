# AES Plan Spec — T035 Loading States

## 1. Sumário Executivo
Adicionar estados de loading consistentes em todas as mutações do frontend.

## 2. Mudanças no Frontend
- `Disputes.tsx`: loading ao submeter e aceitar/rejeitar
- `TeacherCalendar.tsx`: loading ao salvar indisponibilidade (já existe, verificar consistência)
- Botões desabilitados durante loading
- Feedback visual (spinner ou texto)

## 5. Critérios de Aceitação
- Todas as mutações têm loading
- `make lint` e `make test` passam
