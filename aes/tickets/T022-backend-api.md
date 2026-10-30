# Ticket T022 — Backend API FastAPI + autenticação JWT + RBAC

## Contexto
O solver Python existente é exposto como biblioteca. Para a plataforma web, precisamos de uma API REST que permita ao frontend gerir entidades, utilizadores, executar o solver e armazenar resultados. A autenticação JWT e o RBAC (admin/docente/estudante/coordenador) são essenciais para isolar dados por instituição.

## Objetivo
Implementar `backend/` com FastAPI contendo:
- Autenticação JWT (registro, login, refresh)
- RBAC com papéis: admin, docente, estudante, coordenador
- CRUD de entidades: utilizadores, salas, disciplinas, turmas, cursos, professores
- Endpoint para executar o solver (Tabu Search / Simulated Annealing / CP-SAT) de forma assíncrona
- Armazenamento de versões de horário (rascunho, publicado, arquivado)
- Endpoint de exportação (JSON/CSV/iCal)

## Critérios de Aceitação
1. `backend/app/main.py` com FastAPI configurado
2. Endpoint `POST /auth/register` e `POST /auth/login` retornam JWT
3. Middleware de RBAC que bloqueia endpoints por papel
4. CRUD completo para salas, disciplinas, turmas, cursos
5. Endpoint `POST /solver/run` que aceita dataset e retorna horário (assíncrono)
6. Endpoint `GET /schedule/versions` para listar versões de horário
7. Testes de unidade e integração para a API
8. `make test` passa no backend
9. `make lint` passa (ruff)

## Riscos (Hostile Analysis)
- JWT expirado ou tokens reutilizados → mitigação: expiração curta + refresh tokens
- Escalada de privilégio (docente acede a endpoints de admin) → mitigação: dependency de verificação de papel em cada rota
- Solver travando em problemas grandes → mitigação: execução assíncrona com timeout e task ID para polling
- Injeção SQL → mitigação: SQLAlchemy com parâmetros parametrizados

## Fase atual
Plan → Build.
