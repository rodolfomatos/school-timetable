---
ticket: T064
title: Login falhava fora de localhost (API baked + CORS + cookies Secure)
sprint: hotfix
priority: high
status: done
created: 2026-11-02
---

# T064 — "Erro ao fazer login" via IP externo

## Sintoma

`http://193.137.36.111:3000/login` → "Erro ao fazer login" com
`admin@escola.pt`.

## Reprodução (Playwright)

Playwright confirmou:

```
ABORTED http://localhost:8000/auth/login
FAILED POST http://localhost:8000/auth/login -> net::ERR_CONNECTION_REFUSED
UI_ERRORS: ["Erro ao fazer login"]
```

## Causas

1. **API URL baked no build**: `web/src/services/api.ts` usava
   `http://localhost:8000` por omissão. No browser do utilizador, `localhost`
   é o PC dele, não o servidor.
2. **CORS**: `allow_origins` só cobria `localhost:3000`; mesmo com URL
   acessível, o origem `http://193.137.36.111:3000` seria bloqueado.
3. **Cookies `Secure` sobre HTTP**: `_cookie_secure()` usava
   `ENVIRONMENT == production`, mas a stack é servida em HTTP simples. O
   browser descarta cookies `Secure` em HTTP → sessão não persistia.
4. **Sem rehidratação**: `authStore` é só memória; um reload autenticado
   voltava para `/login` apesar do cookie válido.

## Alterações

- `web/src/services/api.ts`: base URL passa a `/api` (same-origin).
- `web/vite.config.ts`: proxy `/api` → `localhost:8000` com remoção do prefixo.
- `docker/nginx.conf`: `location /api/` com `proxy_pass http://backend:8000/`
  (remove `/api`).
- `backend/app/api/routers/auth.py`: `Secure` do cookie derivado do esquema de
  `FRONTEND_URL` (`https://` → `Secure`).
- `web/src/App.tsx`: rehidrata a sessão com `GET /users/me` no arranque.
- `web/src/services/api.ts`: o interceptor 401 não redireciona na sonda
  `/users/me` (evita loop em `/login`).

## Verificação (Playwright, via IP externo)

| Cenário | Resultado |
|---------|-----------|
| Login `admin@escola.pt` | `/dashboard` |
| Reload autenticado | `/dashboard` |
| `/dashboard` sem sessão | `/login` (sem loop) |
| Hosts contactados | apenas `193.137.36.111:3000` |
| Cookies | `access_token`/`refresh_token`, `secure=false` |

## Notas

- Para deploy HTTPS, definir `FRONTEND_URL=https://...` para reactivar cookies
  `Secure`.
- `VITE_API_BASE_URL` continua disponível para deploy com origem separada
  (requer CORS correspondente).
