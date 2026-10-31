# Shadow Doc SD-BUILD-024 — T048 Fase 1: Bootstrap e imports do backend

## Proveniência
Fase 1 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Garantir que a aplicação FastAPI importa e arranca sem erros de importação ou ciclos.

## Decisões tomadas
- Corrigir importações de Role para o módulo onde está realmente definido.
- Garantir que todos os routers que anotam User importam correctamente User.
- Importar select em app/core/deps.py.
- Remover ciclo main.py ↔ schedules.py movendo o limiter para módulo independente.

## Escore epistémico
Alta confiança — baseada na análise de importações e dependências do código.

## Próximos passos
- T049: Integridade do modelo SQLAlchemy
