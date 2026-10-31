# AES Plan Spec — T058 Fase 7: Multi-tenancy, migrações e produção

## 1. Sumário Executivo
Garantir isolamento institucional real, evolução segura do schema e configuração de produção fail-closed.

## 2. Objetivo
- Definir modelo de tenancy: instituição como tenant ou outra fronteira formal.
- Aplicar filtro tenant em todas as queries, jobs, exports e recursos relacionados.
- Derivar tenant do contexto autenticado; nunca confiar apenas em parâmetro fornecido pelo cliente.
- Impedir acesso cruzado por IDs adivinhados.
- Criar Alembic (alembic.ini, env.py, migrations) e retirar create_all como mecanismo de migração em produção.
- Falhar o arranque de produção quando secrets/passwords de desenvolvimento são usados ou estão ausentes.
- Rever exposição de PostgreSQL, CORS, cookies, headers e logs.
- Documentar backup, restore e migração de versão.

## 3. Critérios de Aceitação
[ ] Utilizador da instituição A não lista/lê/altera dados da instituição B.
[ ] Testes cobrem todos os routers e jobs multi-tenant.
[ ] Migrations aplicam schema vazio até à versão actual.
[ ] Upgrade e downgrade suportado são testados.
[ ] Produção não arranca com secrets de exemplo.
[ ] PostgreSQL não fica exposto publicamente por defeito.
[ ] Procedimento backup/restore foi ensaiado.

## 4. Fase atual
Plan → Build → Verify.
