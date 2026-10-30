# Ticket T028 — Revisão Hostil de Segurança e UX

## Contexto
Antes de considerar a fase web completa, é necessária uma revisão hostil focada em segurança (autenticação, autorização, injeção, upload de ficheiros) e UX (usabilidade por docentes não-técnicos, acessibilidade).

## Objetivo
Conduzir revisão hostil produzindo findings BLOCKER/MAJOR/MINOR com condições de fechamento verificáveis. Áreas:
- Autenticação JWT (roubo de token, expiração, refresh)
- Autorização RBAC (escalada de privilégio)
- Injeção SQL / NoSQL
- Upload de ficheiros (CSV/Excel de entidades)
- XSS em formulários de contestação
- UX: calendário acessível, contraste de cores, navegação por teclado, feedback de erros

## Critérios de Aceitação
1. Ficheiro `aes/shadow/SD-REVIEW-002.md` com findings e condições de fechamento
2. Todos os findings BLOCKER e MAJOR corrigidos ou com plano de mitigação
3. Relatório de acessibilidade básico (WCAG 2.1 AA)
4. Kanban atualizado com T028 como Concluído

## Fase atual
Plan → Review.
