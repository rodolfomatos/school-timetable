---
ticket: T063
title: Criar contas de utilizador (seed + make targets)
sprint: hotfix
priority: high
status: done
created: 2026-11-02
---

# T063 — Criar contas / seed

## Contexto

Não havia forma prática de criar contas. O login da UI não tem registo e
`/auth/register` força `role=student` e não está exposto no formulário.
`make db-seed` apontava para `backend/scripts/seed.py` inexistente e falhava.

## Alterações

- `backend/scripts/create_user.py` (novo): script assíncrono para criar contas
  diretamente na BD. Cria perfil `Teacher` quando `role=teacher`. Gera
  palavra-passe aleatória se omitida e imprime-a uma única vez. `--if-not-exists`
  para uso idempotente.
- `backend/scripts/seed.py` (novo): idempotente, cria `admin@escola.pt`,
  `professor@escola.pt`, `aluno@escola.pt` com password `senha123`.
- `backend/scripts/__init__.py` (novo).
- `Makefile`: `db-seed`, `create-user`, `create-admin`. Se o backend correr
  em Docker, usa `docker compose exec -T backend ...`, senão usa o `.venv`
  local.
- `backend/docker/Dockerfile.backend`: copia `backend/scripts/` para a imagem.
- `backend/requirements.txt`: pin `bcrypt==4.0.1` (compatível com
  `passlib[bcrypt]` 1.7.4; bcrypt 5.x quebrou `ValueError: password cannot be
  longer than 72 bytes` nas builds atuais).

## Verificação

- `make db-seed` → cria as 3 contas demo.
- `POST /auth/login` com `admin@escola.pt` / `senha123` → 200.
- `make create-admin email=...` e `make create-user ...` funcionam (com
  password gerada quando omitida).
- `make db-seed` idempotente.

## Conta demo (para testar já)

| Email | Role | Password |
|-------|------|----------|
| admin@escola.pt | admin | senha123 |
| professor@escola.pt | teacher | senha123 |
| aluno@escola.pt | student | senha123 |
