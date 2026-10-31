# Ticket T049 — Fase 2: Integridade do modelo SQLAlchemy

## Contexto
Erros de relacionamento ORM: configure_mappers falha, User.unavailabilities aponta para Teacher, NoForeignKeysError.

## Objetivo
Corrigir e validar integralmente o grafo de entidades e relações SQLAlchemy.

## Critérios de Aceitação
[ ] configure_mappers() executa sem excepções.
[ ] Teste cria, consulta, actualiza e elimina entidades relacionadas numa BD de teste.
[ ] Não existem NoForeignKeysError, InvalidRequestError ou warnings relevantes de mapper.
[ ] Relações e cascades estão documentadas.
[ ] Testes cobrem as cardinalidades e integridade referencial.

## Fase atual
Plan → Build → Verify.
