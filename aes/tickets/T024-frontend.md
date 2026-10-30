# Ticket T024 — Frontend React + ilabuporto-design-system

## Contexto
O frontend precisa de ser moderno, responsivo e usar o design system `@ilabuporto/design-system` (React + TypeScript + Tailwind CSS 3). Deve incluir calendário de indisponibilidades, tabelas de horário, formulários de restrições, portal de contestações e dashboard administrativo.

## Objetivo
Criar `web/` com:
- React + Vite + TypeScript
- `@ilabuporto/design-system` como biblioteca de componentes
- Tailwind CSS 3 com os tokens do design system (brand #009FDF, accent, destructive, warning, info)
- Páginas: Login, Dashboard Admin, Calendário Docente, Tabela de Horário, Portal de Contestações, Gestão de Utilizadores/Salas/Discplinas
- Integração com a API FastAPI via `axios` ou `fetch`
- Gestão de estado com Zustand ou React Context
- Dark mode baseado em classe CSS (`dark` no `<html>`)

## Critérios de Aceitação
1. `web/package.json` com `@ilabuporto/design-system`, `react`, `typescript`, `vite`, `tailwindcss`
2. `web/src/main.tsx` com import de `@ilabuporto/design-system/styles.css`
3. Página de login funcional (autenticação JWT)
4. Página de calendário docente (marcar indisponibilidades com justificação)
5. Página de tabela de horário (visualizar por turma/docente/sala)
6. Página de contestações (submeter, aceitar/rejeitar)
7. Página de dashboard admin (estatísticas, gestão de entidades)
8. Componentes reutilizáveis do design system usados (Button, Badge, Card, Table, Modal, ConfirmDialog, Sidebar, AppShell, Input, Select)
9. Testes de unidade para componentes críticos (vitest)
10. `make lint` passa (eslint + prettier)

## Riscos (Hostile Analysis)
- XSS em campos de texto → mitigação: sanitização de entrada + React escapa por defeito
- CSRF em chamadas à API → mitigação: cookies httpOnly + tokens CSRF
- Dados sensíveis expostos no frontend → mitigação: não guardar tokens em localStorage, usar memória ou httpOnly cookies
- Design system não carrega estilos → mitigação: importar `styles.css` no entry point

## Fase atual
Plan → Build.
