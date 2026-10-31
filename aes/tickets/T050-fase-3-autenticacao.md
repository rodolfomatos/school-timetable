# Ticket T050 — Fase 3: Autenticação e privilégios

## Contexto
Registo público permite criar admin/casual; IDs hard-coded; cookies inseguros.

## Objetivo
Impedir auto-elevação de privilégios e garantir que a identidade autenticada é a fonte de autoridade.

## Critérios de Aceitação
[ ] Tentativa de registo com role=admin não cria administrador.
[ ] Tentativa de registo com role=coordinator não cria coordenador.
[ ] Só actor autorizado altera papéis.
[ ] Operações de resolução guardam o ID do utilizador autenticado.
[ ] Testes negativos cobrem escalada horizontal e vertical.
[ ] Configuração de cookies é segura em produção e testável em ambiente local.
[ ] Eventos sensíveis ficam auditados.

## Fase atual
Plan → Build → Verify.
