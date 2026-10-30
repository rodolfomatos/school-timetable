# AES Plan Spec — T026 Docker Compose

## 1. Sumário Executivo
Orquestração de todos os serviços com Docker Compose para instalação local (on-premise) ou SaaS.

## 2. Serviços
- **backend**: FastAPI + Python + OR-Tools (porta 8000)
- **frontend**: React + Vite build + nginx (porta 3000)
- **postgres**: PostgreSQL 15+ (porta 5432)
- **solver-worker**: Python worker para execução assíncrona do solver (opcional, separável)

## 3. Ficheiros
- `docker-compose.yml` — orquestração com health checks, depends_on, volumes
- `docker/Dockerfile.backend` — multi-stage: build deps + runtime
- `docker/Dockerfile.frontend` — build Vite + nginx serve
- `docker/Dockerfile.worker` — worker assíncrono
- `.env.example` — SECRET_KEY, DATABASE_URL, SOLVER_TIMEOUT, FRONTEND_URL, BACKEND_URL
- `docker/init-db.sql` — script de inicialização da base de dados (opcional)

## 4. Variáveis de Ambiente
- `SECRET_KEY` — chave JWT
- `DATABASE_URL` — conexão PostgreSQL
- `SOLVER_TIMEOUT` — segundos máximos para o solver (default 60)
- `FRONTEND_URL` — URL do frontend (para CORS)
- `BACKEND_URL` — URL do backend (para o frontend)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

## 5. Health Checks
- Backend: `GET /health` → 200
- Frontend: `GET /` → 200
- Postgres: `pg_isready`

## 6. Scripts
- `docker/entrypoint.sh` — aguarda DB, executa migrações Alembic, inicia o servidor
- `docker/seed.sh` — opcional: carrega dados de exemplo

## 7. Documentação
- `README.md` atualizado com instruções `docker compose up --build`
- Instruções para produção (variáveis de ambiente seguras, reverse proxy)
