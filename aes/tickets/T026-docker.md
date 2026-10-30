# Ticket T026 — Docker Compose (On-Premise / SaaS)

## Contexto
A plataforma deve ser instalável localmente por uma escola (on-premise) ou disponibilizada como SaaS. Docker Compose é a escolha para simplicidade de implantação local.

## Objetivo
Criar `docker/` com:
- `docker-compose.yml`: backend (FastAPI), frontend (React + nginx), postgres, solver-worker
- `Dockerfile.backend`: Python + dependências + OR-Tools
- `Dockerfile.frontend`: Node + Vite build + nginx serve
- `Dockerfile.worker`: Python worker para execução assíncrona do solver
- `.env.example`: variáveis de ambiente (SECRET_KEY, DATABASE_URL, SOLVER_TIMEOUT)
- Script de inicialização que cria tabelas e dados de exemplo

## Critérios de Aceitação
1. `docker-compose.yml` orquestra todos os serviços
2. `docker compose up` levanta a aplicação completa
3. Acessível em `localhost:3000` (frontend) e `localhost:8000` (API)
4. Base de dados persistente via volume Docker
5. Variáveis de ambiente em `.env`
6. Health checks para todos os serviços
7. Documentação no `README.md` com instruções de `docker compose up`

## Riscos (Hostile Analysis)
- Porta já em uso → mitigação: portas configuráveis via .env
- Base de dados não inicia antes do backend → mitigação: health checks + depends_on com condition
- Build do frontend falha por variáveis de build ausentes → mitigação: argumentos de build no Dockerfile
- OR-Tools pesado na imagem → mitigação: imagem multi-stage ou worker separado

## Fase atual
Plan → Build.
