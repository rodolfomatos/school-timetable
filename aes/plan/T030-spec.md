# AES Plan Spec — T030 JWT httpOnly

## 1. Sumário Executivo
Mudar autenticação de localStorage para cookies httpOnly para prevenir roubo de token por XSS.

## 2. Mudanças no Backend
- `POST /auth/login`: definir cookie `access_token` com `HttpOnly`, `Secure`, `SameSite=Lax`
- `POST /auth/refresh`: renovar cookie httpOnly
- `POST /auth/logout`: limpar cookie `access_token`
- Middleware: ler token do cookie em vez do header Authorization (ou suportar ambos)

## 3. Mudanças no Frontend
- `web/src/stores/authStore.ts`: remover `persist` para token; armazenar apenas em memória
- `web/src/services/api.ts`: configurar `withCredentials: true` no axios
- Frontend não armazena token em localStorage

## 4. Testes
- Teste de login verifica que cookie é definido
- Teste de logout verifica que cookie é limpo

## 5. Critérios de Aceitação
- Cookie httpOnly definido no login
- Frontend não usa localStorage para token
- `make test` e `make lint` passam
