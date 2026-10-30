# Ticket T035 — Fix F-017 (MINOR): Loading states consistentes

## Contexto
Finding F-017 (MINOR): Algumas ações (ex: salvar indisponibilidade) mostram loading, outras não (ex: submeter contestação, aceitar/rejeitar).

## Objetivo
Adicionar estados de loading consistentes em todas as mutações:
- Frontend: adicionar `loading` state em todas as mutações (submeter contestação, aceitar/rejeitar, salvar indisponibilidade, gerar horário)
- Feedback visual ao usuário durante processamento
- Desabilitar botões durante o loading

## Critérios de Aceitação
1. Todas as mutações têm estado de loading
2. Botões desabilitados durante o loading
3. Feedback visual (spinner ou texto "A processar...")
4. `make lint` e `make test` passam

## Fase atual
Plan → Build.
