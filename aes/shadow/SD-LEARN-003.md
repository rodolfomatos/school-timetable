# Shadow Doc SD-LEARN-003 — Aprendizados da Fase Web

## Proveniência
Learn phase dos tickets T022-T026, concluída em 30/10/2026.

## Aprendizados Técnicos

### 1. Integração do `ilabuporto/design-system`
- Biblioteca React com TypeScript + Tailwind CSS 3
- Tokens de cor institucionais U.Porto (brand #009FDF)
- Componentes prontos: AppShell, Sidebar, Navbar, Table, Modal, ConfirmDialog, Input, Select, Button, Badge, Card, StatCard
- Dark mode por classe CSS (`dark` no `<html>`)
- É necessário importar `styles.css` no entry point para funcionalidade completa

### 2. FastAPI + SQLAlchemy 2.0 Async
- Bom para expor o solver Python existente como API
- Pydantic v2 para validação de dados
- Alembic para migrações (configurado, não testado)
- Execução assíncrona do solver em ThreadPool para não bloquear a API

### 3. JWT + RBAC
- Tokens de acesso curtos (30 min) + refresh tokens (7 dias)
- Papéis: admin, teacher, student, coordinator
- Dependências FastAPI (`Depends`) para verificação de papel

### 4. Docker Compose
- Orquestração simples: postgres + backend + frontend
- Health checks para ordenação de inicialização
- Volumes para persistência de dados

## Decisões de Design

1. **Frontend separado do backend** — Permite implantação independente e escalabilidade
2. **Design system institucional** — Consistência visual com U.Porto, reduz tempo de design
3. **Solver como serviço** — Separação de preocupações: API gerencia, solver calcula

## Limitações Atuais

- O solver service usa armazenamento em memória para tarefas (não persistente)
- As migrações Alembic estão configuradas mas não testadas
- O frontend usa mock de dados em algumas partes (integração completa com API pendente)
- Testes E2E criados mas não executados contra instância ao vivo

## Próximos Passos

- Executar testes E2E com Playwright contra instância ao vivo
- Executar revisão hostil de segurança (T028)
- Capturar métricas de desempenho do solver com dados reais de faculdade
