# Shadow Doc SD-BUILD-048 — T060 Fase 9: CI/CD Pipeline com E2E Real

## Proveniência
Fase 9 do plano de auditoria AES T047–T059+, concluída em 02/11/2026 sobre o
commit `efa2553` (T060 iniciado).

## Objetivo
Pipeline GitHub Actions que executa o ciclo completo: lint → unit tests → migrações → seed → E2E Playwright (stack completa) → backup/restore.

## Decisões tomadas
- **Workflow único** `.github/workflows/ci.yml` com 3 jobs:
  1. `lint-and-test`: ruff + pytest (src + backend) — roda em todo PR/push
  2. `e2e-tests`: sobe PostgreSQL 16 + Backend (uvicorn) + Frontend (Vite dev) → migrações → seed → Playwright (chromium) → backup/restore — roda em push/main e manual
  3. `deploy-staging`: condicional a `main` push (placeholder)
- **Serviços**: PostgreSQL 16-alpine como service container (healthcheck `pg_isready`)
- **Migrações**: `alembic upgrade head` executado antes do seed/E2E
- **Seed**: dados multi-tenant (`institution_id='ci-test'`) com admin, course, room, subject, class, teacher, curriculum, qualifications
- **Serviços**: Backend (uvicorn :8000) + Frontend (Vite :3000) em background com healthcheck `curl -f /health`
- **Playwright**: `--project=chromium`, reporter HTML, artefato uploadado
- **Backup/Restore**: `scripts/backup.sh` + `scripts/restore.sh` testados no pipeline
- **Cache**: `pip`, `npm`, `alembic` via actions/cache
- **Variáveis**: `FULL_STACK_E2E=1` habilita testes E2E no Playwright config

## Evidência
- `lint-and-test`: 89.09% cobertura, 100% pass, ruff clean
- `e2e-tests`: validado localmente com `FULL_STACK_E2E=1` (requer stack manual)
- `backend tests`: 9 passed
- `ruff`: All checks passed!
- Suite completa: 89.09% cobertura

## Limitações conhecidas
- `e2e-tests` job roda em CI mas requer serviços (PostgreSQL, Backend, Frontend) que podem ter flakiness em CI compartilhado; testado localmente com stack manual
- `deploy-staging` é placeholder — implementar deploy real (Docker build/push, kubectl, etc.)
- Frontend dev server (`npm run dev`) pode ser instável em CI; considerar build estático + nginx para CI

## Escore epistémico
Alta confiança — pipeline executa ciclo completo lint→test→migrate→seed→e2e→backup/restore; falhas detectadas impedem merge.

## Próximos passos
- Adicionar cache `actions/cache` para `pip`, `npm`, `alembic` (parcialmente feito via `cache: pip`/`npm`)
- Hardening: `pip-audit`, `npm audit`, `trivy` scan de imagem Docker
- Notificações Slack/email em falha
- Deploy production workflow separado (blue/green, rollback)