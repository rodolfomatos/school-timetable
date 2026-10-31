# Ticket T051 — Fase 3: Modelo de domínio e integração

## Contexto
O solver recebe todas as turmas com todas as disciplinas; não há relação curricular; qualificações docentes não chegam da aplicação.

## Objetivo
Criar uma camada de domínio canónica, independente do ORM, que traduza os dados institucionais num problema de timetabling completo e consistente.

## Critérios de Aceitação
[ ] O solver recebe um ProblemInstance/DTO sem dependência de sessão ORM.
[ ] Só são criadas sessões para relações curriculares válidas.
[ ] Docentes não qualificados não são elegíveis.
[ ] Indisponibilidades persistidas e adicionais são aplicadas.
[ ] Capacidade e requisitos de sala são transportados para o domínio.
[ ] Dados incompletos produzem diagnóstico explícito.
[ ] Testes provam que não há mistura de cursos/turmas/disciplinas.

## Fase atual
Plan → Build → Verify.
