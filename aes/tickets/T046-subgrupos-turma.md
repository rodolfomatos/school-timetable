# Ticket T046 — Suporte a subgrupos de turma (divisão de aulas)

## Contexto
Uma turma pode ser dividida em subgrupos para uma disciplina em particular. Exemplo: disciplina de Música em regime articulado — parte dos alunos tem aula teórica num horário, outra parte tem aula prática noutro horário, e depois trocam. Isto é comum quando não há professores suficientes para todos os alunos simultaneamente.

## Objetivo
Adicionar entidade `Subgrupo` ao modelo de domínio e atualizar:
- `Aula` para incluir opcionalmente um `subgrupo_id`
- `H03` (turma não tem duas aulas no mesmo slot) para considerar subgrupos (duas aulas da mesma turma podem ocorrer no mesmo slot se forem de subgrupos diferentes)
- CP-SAT para incluir subgrupo nas variáveis de decisão
- Seed para gerar aulas com subgrupos quando aplicável

## Critérios de Aceitação
1. Entidade `Subgrupo` adicionada a `models.py` com: identificador, turma_pai, nome (ex: "Grupo A", "Grupo B"), numero_alunos
2. `Aula` tem campo opcional `subgrupo_id`
3. `H03` verificada por (turma, subgrupo, slot) em vez de apenas (turma, slot)
4. CP-SAT cria variáveis incluindo subgrupo quando aplicável
5. Seed gera aulas com subgrupos quando há mais de um subgrupo para uma disciplina
6. Testes de unidade para subgrupos
7. `make test` e `make lint` passam

## Fase atual
Plan → Build.
