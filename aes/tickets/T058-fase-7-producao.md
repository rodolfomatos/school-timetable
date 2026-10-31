# Ticket T058 — Fase 7: Multi-tenancy, migrações e produção

## Contexto
Institutional ID é decorativo; não há migrações Alembic; credenciais de desenvolvimento permitidas em produção; não há isolamento institucional nas consultas.

## Objetivo
Garantir isolamento institucional real, evolução segura do schema e configuração de produção fail-closed.

## Critérios de Aceitação
[ ] Utilizador da instituição A não lista/lê/altera dados da instituição B.
[ ] Testes cobrem todos os routers e jobs multi-tenant.
[ ] Migrations aplicam schema vazio até à versão actual.
[ ] Upgrade e downgrade suportado são testados.
[ ] Produção não arranca com secrets de exemplo.
[ ] PostgreSQL não fica exposto publicamente por defeito.
[ ] Procedimento backup/restore foi ensaiado.

## Fase atual
Plan → Build → Verify.
