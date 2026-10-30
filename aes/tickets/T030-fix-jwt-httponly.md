# Ticket T030 — Fix F-012 (BLOCKER): JWT em cookies httpOnly

## Contexto
Finding F-012 (BLOCKER): O token JWT é armazenado em localStorage via Zustand `persist()`, o que expõe o token a roubo por XSS.

## Objetivo
Mudar a autenticação para usar cookies httpOnly:
- Backend: definir `access_token` como cookie httpOnly na resposta de login/refresh
- Backend: endpoint `/auth/logout` para limpar o cookie
- Frontend: remover `persist` do Zustand para o token; usar cookies via axios com `withCredentials: true`
- Frontend: ler o utilizador do endpoint `/users/me` em vez de armazenar no localStorage

## Critérios de Aceitação
1. `POST /auth/login` define cookie `access_token` com `HttpOnly`, `Secure`, `SameSite=Lax`
2. `POST /auth/refresh` renova o cookie httpOnly
3. `POST /auth/logout` limpa o cookie
4. Frontend não armazena token em localStorage (remover `persist` do authStore)
5. Frontend envia `withCredentials: true` nas requisições axios
6. Testes de unidade para login/logout com cookie
7. `make test` e `make lint` passam

## Riscos (Hostile Analysis)
- CSRF com cookies httpOnly → mitigação: SameSite=Lax + token CSRF opcional
- Token não acessível via JS → mitigação: usar endpoint `/users/me` para obter perfil

## Fase atual
Plan → Build.
