# Ticket T032 — Fix F-014 (MAJOR): Rate limiting no solver

## Contexto
Finding F-014 (MAJOR): Endpoint `POST /scheduler/run` não tem limite de requisições, permitindo DoS através de múltiplas execuções do solver (processo computacionalmente pesado).

## Objetivo
Adicionar rate limiting no endpoint do solver:
- Backend: instalar `slowapi` e adicionar limite de requisições por IP/usuário
- Limite: ex. 5 requisições por minuto por IP para o endpoint do solver
- Retornar 429 (Too Many Requests) quando excedido
- Testes: verificar que o limite é aplicado

## Critérios de Aceitação
1. `slowapi` instalado no backend
2. Rate limit configurado em `POST /scheduler/run`
3. Resposta 429 quando excedido
4. Teste de unidade para rate limiting
5. `make test` e `make lint` passam

## Fase atual
Plan → Build.
