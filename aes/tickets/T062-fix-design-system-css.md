---
ticket: T062
title: Design system não carregava em /login (Tailwind não processado)
sprint: hotfix
priority: high
status: done
created: 2026-11-02
---

# T062 — Design system em falta no frontend

## Context

A página `http://<host>:3000/login` respondia 200, mas renderizava sem estilos:
botões, inputs, cards e layout sem formatação.

## Diagnóstico

O CSS servido (`/assets/index-*.css`, ~1.5 KB) continha literalmente
`@tailwind base;@tailwind components;@tailwind utilities;` e não tinha as
variáveis do design system. Duas causas independentes:

1. **Sem `web/postcss.config.*`** — o Vite nunca executou o Tailwind, pelo que
   nenhuma classe utilitária (`.fixed`, `.bg-gray-50`, `.px-4`, …) foi gerada.
   Os componentes React usam essas classes intensivamente.
2. **`@import "@/design-system/styles.css"` depois das diretivas `@tailwind`** —
   um `@import` só é válido antes de todas as outras regras; o Vite descartou-o
   silenciosamente, pelo que `.btn`, `.card`, `--color-brand`, etc. também não
   chegavam ao browser.

## Alterações

- `web/postcss.config.js` (novo): plugins `tailwindcss` + `autoprefixer`.
- `web/src/index.css`: `@import "./design-system/styles.css";` movido para o
  topo, antes de `@tailwind`.

## Verificação

- CSS de produção passou de ~1.5 KB para ~33 KB.
- Contém `--color-brand` (design system) e utilitários como `.fixed`.
- Já não contém `@tailwind` literal.
- `GET /login` = 200 e CSS = 200 (33 KB) via IP externo.

## Riscos / follow-up

- Não existe teste automatizado que garanta que as classes Tailwind são
  geradas; uma regressão silenciosa é possível. Candidato a teste E2E de
  computed styles.
- `web/tailwind.config.ts` referencia `node_modules/@ilabuporto/design-system`,
  pacote que não existe (o DS é local em `web/src/design-system`). Referência
  inofensiva, mas enganadora.
