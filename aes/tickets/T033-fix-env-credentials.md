# Ticket T033 — Fix F-015 (MAJOR): Credenciais no .env.example

## Contexto
Finding F-015 (MAJOR): Ficheiro `docker/.env.example` contém credenciais em texto simples (`POSTGRES_PASSWORD=school`, `SECRET_KEY=dev-secret-key`), que podem ser commitadas acidentalmente.

## Objetivo
- Remover valores reais do `.env.example`, deixar apenas placeholders
- Adicionar `.env` ao `.gitignore` (se ainda não estiver)
- Adicionar nota no README sobre variáveis obrigatórias em produção

## Critérios de Aceitação
1. `docker/.env.example` contém apenas placeholders (ex: `SECRET_KEY=sua-chave-secreta-aqui`)
2. `.env` está no `.gitignore`
3. README documenta variáveis obrigatórias para produção
4. `make lint` passa

## Fase atual
Plan → Build.
