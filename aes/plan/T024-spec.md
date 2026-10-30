# AES Plan Spec — T024 Frontend React + ilabuporto-design-system

## 1. Sumário Executivo
Frontend React + Vite + TypeScript usando `@ilabuporto/design-system` e Tailwind CSS 3. Consome a API FastAPI.

## 2. Stack
- React 18+, TypeScript, Vite
- `@ilabuporto/design-system` (componentes UI)
- `tailwindcss` (estilização)
- `axios` ou `fetch` (cliente API)
- `zustand` ou `react-context` (gestão de estado)
- `react-router-dom` (roteamento)
- `vitest` + `react-testing-library` (testes de unidade)
- `eslint` + `prettier` (lint/format)

## 3. Estrutura de Diretórios
```
web/
  src/
    main.tsx              # Entry point, import styles.css do design system
    App.tsx               # Roteador principal
    pages/
      Login.tsx           # Página de login
      Dashboard.tsx       # Dashboard admin (estatísticas, gestão)
      TeacherCalendar.tsx # Calendário de indisponibilidades (docente)
      ScheduleTable.tsx   # Tabela de horário (turma/docente/sala)
      Disputes.tsx        # Portal de contestações
      ManageUsers.tsx     # Gestão de utilizadores (admin)
      ManageRooms.tsx     # Gestão de salas (admin)
      ManageSubjects.tsx  # Gestão de disciplinas (admin)
      ManageClasses.tsx   # Gestão de turmas (admin)
    components/
      ScheduleGrid.tsx    # Grid de horário reutilizável
      AvailabilityPicker.tsx # Seletor de slots indisponíveis
      DisputeCard.tsx     # Card de contestação
      RoleGuard.tsx       # Componente que bloqueia por papel
    hooks/
      useAuth.tsx         # Autenticação (token, login, logout)
      useApi.tsx          # Chamadas à API
      useSchedule.tsx     # Estado do horário
    services/
      api.ts              # Instância axios com interceptores de auth
    types/
      index.ts            # Tipos TypeScript compartilhados
    stores/
      authStore.ts        # Estado de autenticação
      scheduleStore.ts    # Estado do horário
    utils/
      formatters.ts       # Formatação de datas, slots
  tailwind.config.ts
  tsconfig.json
  vite.config.ts
  index.html
```

## 3. Páginas e Funcionalidades
- **Login**: email/senha, guarda JWT em memória (ou httpOnly cookie via API)
- **Dashboard Admin**: cards de estatística (StatCard), tabela de entidades recentes, botão gerar horário
- **TeacherCalendar**: calendário semanal, clicar em slot → modal com justificativa pré-definida → salvar indisponibilidade
- **ScheduleTable**: grid por turma/docente/sala, cores por disciplina, clicar em aula → detalhes + contestar
- **Disputes**: lista de contestações (docente vê as suas; admin vê todas pendentes), botões aceitar/rejeitar (admin)
- **ManageUsers/Rooms/Subjects/Classes**: tabelas com CRUD (Table + Modal + ConfirmDialog do design system)

## 4. Componentes do Design System Usados
- `Button` (primary, secondary, destructive, ghost)
- `Badge` (status: success, error, warning, info, neutral)
- `Card` (content container)
- `ConfirmDialog` (confirmação de exclusão/aceitação)
- `Input` / `Select` (formulários)
- `Modal` (formulários de entidade)
- `Pagination` (tabelas grandes)
- `Sidebar` (navegação admin)
- `AppShell` (layout admin: sidebar + conteúdo)
- `Brand` / `Navbar` / `Footer` (identidade institucional)
- `Table` (dados de entidades e horários)
- `Tabs` (navegação entre visualizações de horário)
- `Toggle` (interruptores para preferências)
- `SlideInPanel` (painel lateral para detalhes de aula)

## 5. Tokens de Cor
- `brand` (#009FDF) — ações institucionais, primário
- `destructive` (#ef4444) — erros, rejeições
- `warning` (#eab308) — avisos, pendentes
- `info` (#3b82f6) — informações gerais
- `accent` (#22c55e) — sucesso, confirmações neutras

## 6. Testes
- `web/src/components/__tests__/ScheduleGrid.test.tsx` — renderização do grid
- `web/src/components/__tests__/AvailabilityPicker.test.tsx` — seleção de slots
- `web/src/pages/__tests__/Login.test.tsx` — autenticação
- Cobertura de componentes críticos

## 7. Quality Gates
- `make lint` passa (eslint + prettier)
- `make test` passa (vitest)
- Build Vite passa sem erros
