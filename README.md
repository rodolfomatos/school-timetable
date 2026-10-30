# README — School Timetable (Plataforma Web)

# school-timetable

Gerador de horários escolares com plataforma web completa, baseado em práticas de engenharia AES e na literatura de automated timetabling.

## O que é

É um sistema completo para geração e gestão de horários escolares/académicos, com:
- **Solver Python** (Tabu Search, Simulated Annealing, CP-SAT/OR-Tools)
- **API REST FastAPI** com autenticação JWT e RBAC
- **Frontend React** com design system `@ilabuporto/design-system` (U.Porto)
- **Docker Compose** para instalação local ou SaaS
- **Testes E2E com Playwright**

## Estrutura
```
school-timetable/
├── src/timetable/          # Solver Python (core)
├── backend/                # API FastAPI + autenticação + RBAC
├── web/                    # Frontend React + design system
├── e2e/                    # Testes Playwright
├── docker/                 # Dockerfiles + docker-compose
├── aes/                    # Artefatos do sistema AES
├── docs/                   # Documentação técnica
├── tests/                  # Testes unitários Python
└── data/                   # Dados de exemplo
```

## Começar (Desenvolvimento Local)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API disponível em `http://localhost:8000` (docs em `/docs`)

### Frontend
```bash
cd web
npm install
npm run dev
```
Frontend disponível em `http://localhost:3000`

### Com Docker (Recomendado)
```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## Personas e Fluxos

| Persona | O que pode fazer |
|---------|------------------|
| **Docente** | Marcar indisponibilidades no calendário com justificação; contestar slots atribuídos; ver o seu horário |
| **Admin** | Gerir utilizadores, salas, disciplinas, turmas; gerar horário; aceitar/rejeitar contestações; publicar |
| **Coordenador** | Mesmas permissões de admin para gestão de entidades |
| **Estudante** | Ver horário da sua turma; receber notificações de alterações |

## Documentação Técnica
- `docs/literature_review.md` — papers e referências sobre timetabling
- `docs/architecture.md` — arquitetura de software
- `docs/constraints.md` — catálogo de restrições duras e moles (incluindo faculdade)
- `docs/QUALITY_GATES.md` — quality gates do projeto AES
- `aes/kanban.md` — quadro de tickets AES
- `aes/shadow/` — shadow docs com decisões e escore epistémico

## Testes
```bash
# Testes Python (backend + solver)
cd /opt/school-timetable
make test          # 80+ testes, cobertura ≥ 80%
make lint          # ruff

# Testes E2E (frontend web)
cd e2e
npm install
npx playwright install
npm test           # Playwright headless
```

## License

MIT
