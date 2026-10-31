# Ticket T050 — Fase 3: Autenticação e privilégios

## Contexto
O registo público permitia ao cliente escolher `role` (incluindo `coordinator` e
`teacher`), o `resolved_by` de contestações era o valor hard-coded `1`, e os
cookies de autenticação tinham `secure=False` fixo. Faltava ainda auditoria de
eventos sensíveis.

## Objetivo
Impedir auto-elevação de privilégios e garantir que a identidade autenticada é a
única fonte de autoridade.

## Causa-raiz (confirmada)
1. `backend/app/api/routers/auth.py`: `role = user_in.role` era persistido
   directamente; apenas `admin` era bloqueado.
2. `backend/app/api/routers/disputes.py`: `dispute.resolved_by = 1  # TODO`.
3. `auth.py`: `secure=False` e `max_age` hard-coded; o login nem sequer definia
   o cookie de refresh, tornando `/auth/refresh` inútil no fluxo por cookie.
4. Ausência de logging de registo, login falhado, refresh, logout e resolução de
   contestações.

## Correções aplicadas
- Registo público força sempre `Role.STUDENT`; tentativas de papel elevado são
  registadas em log e ignoradas.
- `PATCH /disputes/{id}` recebe `current_user` via `require_role(Role.ADMIN)` e
  grava `dispute.resolved_by = current_user.id`.
- Cookies `access_token` e `refresh_token` usam `HttpOnly`, `SameSite=Lax`,
  `Secure` quando `ENVIRONMENT=production`, e expiração derivada de `settings`.
- Login passa a emitir access + refresh cookie; refresh usa o mesmo helper.
- Logging de eventos sensíveis sem dados pessoais desnecessários (apenas IDs).
- Criação/alteração de papéis continua restrita a admin (`PATCH /users/{id}`).

## Critérios de Aceitação
- [x] Tentativa de registo com `role=admin` não cria administrador.
- [x] Tentativa de registo com `role=coordinator` não cria coordenador.
- [x] Só actor autorizado altera papéis.
- [x] Operações de resolução guardam o ID do utilizador autenticado.
- [x] Testes negativos cobrem escalada horizontal e vertical.
- [x] Configuração de cookies é segura em produção e testável em ambiente local.
- [x] Eventos sensíveis ficam auditados (logging estruturado).

## Evidência de regressão
- Antes da correcção (worktree em `4842875`, com os mesmos testes):
  `6 failed, 1 passed`.
- Depois da correcção: `9 passed`.
- `ruff check src tests backend/app backend/tests` → `All checks passed!`.
- `from app.main import app` → `APP_IMPORT_OK 14`.
- Suite canónica → 90.59% de cobertura.

## Decisão documentada sobre CSRF
A autenticação por cookie usa `SameSite=Lax`, que impede o envio do cookie em
POST cross-site, e CORS não usa wildcard. Não foi introduzido token CSRF
double-submit para não quebrar o contrato actual do frontend; fica registado como
trabalho futuro caso o frontend passe a permitir fluxos cross-site.

## Estado epistémico
- Implementado: **SIM**
- Testado: **SIM**
- Verificado: **SIM** (execução real via ASGI + SQLite)
- Independentemente verificado: **PENDENTE** (T059)

## Fase actual
Plan → Build → Verify → Review (concluído) → Learn.
