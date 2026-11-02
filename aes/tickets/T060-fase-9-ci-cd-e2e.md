# Ticket T060 — Fase 9: CI/CD Pipeline com E2E Real

## Contexto
Testes E2E Playwright existem mas requerem `FULL_STACK_E2E=1` (stack completa rodando). Não há pipeline CI que suba stack completa e rode testes.

## Objetivo
Pipeline GitHub Actions que:
1. Sobe PostgreSQL + Backend + Frontend dev server
2. Roda migrações Alembic
5. Semeia dados de teste
6. Roda testes E2E Playwright (`FULL_STACK_E2E=1`)
7. Valida backup/restore no pipeline

## Critérios de Aceitação
- [ ] Workflow `.github/workflows/ci.yml` roda em PRs e push to main
- [ ] Sobe PostgreSQL 16 + Backend (FastAPI) + Frontend (Vite dev server)
- [ ] Roda `alembic upgrade head` antes dos testes
- [ ] Semeia dados de teste multi-tenant
- [ ] Roda `npx playwright test --project=chromium` com `FULL_STACK_E2E=1`
- [ ] Testa backup/restore no pipeline
- [ ] Falha o build se qualquer teste falhar
- [ ] Cache de dependências (npm, pip, alembic)

## Fase atual
Plan → Build → Verify

## Rigor AES
- Testes de regressão: falhar antes, passar depois
- Cobertura ≥ 80%
- Lint zero
- Relatório de evidência em `aes/tickets/T060-fase-9-ci-cd-e2e.md`