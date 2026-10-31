# AES Plan Spec — T049 Fase 2: Integridade do modelo SQLAlchemy

## 1. Sumário Executivo
Corrigir e validar integralmente o grafo de entidades e relações SQLAlchemy antes de desenvolver novos fluxos de persistência.

## 2. Objetivo
- Rever Course, Room, Subject, Class, Teacher, User, Unavailability, Dispute, ScheduleVersion e ScheduleAssignment.
- Para cada relationship(back_populates=...), garantir propriedade correspondente e simétrica.
- Garantir que o lado relacional aponta para a entidade certa: User.unavailabilities e User.disputes não podem declarar back_populates="teacher" se o relacionamento pertence a Teacher, salvo se a relação e FK forem redesenhadas explicitamente.
- Garantir ForeignKeys e cardinalidades coerentes.
- Rever cascade, delete-orphan, uselist, nullable e índices.
- Separar perfil de autenticação User do perfil operacional Teacher, com relação 1:0/1 explícita.
- Não criar relações ORM artificiais apenas para silenciar erros.

## 3. Critérios de Aceitação
[ ] configure_mappers() executa sem excepções.
[ ] Teste cria, consulta, actualiza e elimina entidades relacionadas numa BD de teste.
[ ] Não existem NoForeignKeysError, InvalidRequestError ou warnings relevantes de mapper.
[ ] Relações e cascades estão documentadas.
[ ] Testes cobrem as cardinalidades e integridade referencial.

## 4. Fase atual
Plan → Build → Verify.
