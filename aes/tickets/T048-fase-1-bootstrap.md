# Ticket T048 — Fase 1: Bootstrap e imports do backend

## Contexto
Erros de importação de Role, User não importado, select não importado, e dependência circular main.py ↔ schedules.py impedem a aplicação de arrancar.

## Objetivo
Garantir que a aplicação FastAPI importa e arranca sem erros de importação ou ciclos.

## Critérios de Aceitação
[ ] python -c "from app.main import app" termina com exit code 0.
[ ] A aplicação arranca com configuração de teste.
[ ] Todos os routers são registados.
[ ] Um teste de endpoint protegido resolve dependências sem NameError/ImportError.
[ ] Não existe import circular entre main.py, routers e serviços.

## Fase atual
Plan → Build → Verify.
