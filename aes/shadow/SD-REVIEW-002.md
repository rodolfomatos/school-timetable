# Shadow Doc SD-REVIEW-002 — Revisão Hostil de Segurança e UX

## Proveniência
Review phase do ticket T028, concluída em 30/10/2026.

## Veredito Geral
**APROVADO COM CONDIÇÕES** — A arquitetura é sólida, mas existem findings de segurança e UX que devem ser tratados antes do deploy em produção.

## Findings

### F-012 (BLOCKER): JWT armazenado em localStorage no frontend
**Evidência:** `web/src/stores/authStore.ts` usa `persist` do Zustand que armazena no localStorage.
**Risco:** XSS pode roubar o token de acesso.
**Condição de fechamento:** Mover para cookies httpOnly ou adicionar proteção XSS robusta (CSP, sanitização).

### F-013 (MAJOR): Sem validação de entrada em formulários de contestação
**Evidência:** `web/src/pages/Disputes.tsx` aceita texto livre sem sanitização.
**Risco:** XSS refletido quando o admin visualiza a contestação.
**Condição de fechamento:** Adicionar sanitização de entrada (DOMPurify ou similar) e validação no backend.

### F-014 (MAJOR): Solver exposto sem rate limiting
**Evidência:** Endpoint `POST /scheduler/run` não tem limite de requisições.
**Risco:** DoS através de múltiplas execuções do solver (processo pesado).
**Condição de fechamento:** Adicionar rate limiting (ex: slowapi ou Redis-based).

### F-015 (MAJOR): Senhas em texto simples no `.env.example`
**Evidência:** `docker/.env.example` tem `POSTGRES_PASSWORD=school` e `SECRET_KEY=dev-secret-key`.
**Risco:** Credenciais expostas se o ficheiro for commitado.
**Condição de fechamento:** Adicionar `.env.example` ao `.gitexit`, usar variáveis obrigatórias em produção.

### F-016 (MINOR): Contraste de cores em alguns componentes
**Evidência:** Alguns textos em `text-gray-400` sobre fundo escuro podem não atingir WCAG AA.
**Condição de fechamento:** Auditar contraste com ferramenta automatizada (axe-core).

### F-017 (MINOR): Não há feedback de loading em todas as ações
**Evidência:** Algumas ações (ex: salvar indisponibilidade) mostram loading, outras não.
**Condição de fechamento:** Adicionar estados de loading consistentes em todas as mutações.

## Resumo de Severidade

| ID | Severidade | Estado |
|----|-----------|--------|
| F-012 | BLOCKER | Pendente |
| F-013 | MAJOR | Pendente |
| F-014 | MAJOR | Pendente |
| F-015 | MAJOR | Pendente |
| F-016 | MINOR | Pendente |
| F-017 | MINOR | Pendente |

## Próximos Passos

Criar tickets T030-T035 para corrigir os findings acima antes do deploy em produção.
