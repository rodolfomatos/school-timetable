# Ticket T051 — Fase 3: Modelo de domínio e integração

## Contexto
O solver recebia todas as turmas × todas as disciplinas (produto cartesiano); não
havia relação curricular explícita, qualificações docentes não chegavam da
aplicação ao domínio, e indisponibilidades adicionais não eram integradas.

## Objetivo
Criar uma camada de domínio canónica, independente do ORM, que traduza os dados
institucionais num ``ProblemInstance`` completo e consistente.

## Causa-raiz (confirmada)
1. `src/timetable/cp_sat_baseline.py` gerava sessões com duplo loop
   `for turma in turmas: for disc in disciplinas:` — produto cartesiano.
2. `Professor.qualificacoes` existia mas nunca era usada para filtrar variáveis
   no CP-SAT.
3. Nenhuma tabela ORM para currículo (turma-disciplina-docente) nem para
   qualificações (docente-disciplina).
4. Indisponibilidades adicionais passadas via API eram ignoradas no solver
   (`additional_unavailabilities` não utilizado).

## Correções aplicadas
- Novo módulo `src/timetable/domain.py`: `construir_problema()` valida,
  diagnostica e produz `ProblemInstance`.
  - Sessões só para relações curriculares explícitas (`EntradaCurricular`).
  - Docentes elegíveis = fixos na relação curricular OU qualificados para a
    disciplina. Nunca "todos".
  - Indisponibilidades persistidas + adicionais subtraídas da disponibilidade.
  - Capacidade e tipo de sala validados antes de criar sessões.
  - Diagnósticos explícitos (`ERROR` impede execução; `WARNING` avisos).
- `src/timetable/models.py`:
  - `SessaoRequerida`: identidade estável `lesson_id`, professores elegíveis,
    `subgrupo_id`.
  - `Professor.qualificacoes_definidas`: distingue "não especificado" (legacy)
    de "explicitamente vazio".
  - `ContextoRestricoes.sessoes_requeridas`: opcional, para chamadas legacy.
- `src/timetable/cp_sat_baseline.py`:
  - Usa `ctx.sessoes_requeridas` quando presente; mantém produto cartesiano
    legacy como fallback.
  - Variáveis só para docentes elegíveis da sessão (não para todos os
    docentes da disciplina).
  - Mapa `lesson_id -> turma_id` explícito (`sessao_turma`), sem parsing.
- ORM (`backend/app/models/school.py`):
  - `ClassSubject`: relação curricular explícita (turma-disciplina-docente
    opcional).
  - `TeacherSubject`: qualificação explícita docente-disciplina.
- Testes: `tests/test_domain.py` (12 testes cobrindo todos os códigos de
  diagnóstico).

## Critérios de Aceitação
- [x] O solver recebe `ProblemInstance`/`DTO` sem dependência de sessão ORM.
- [x] Só são criadas sessões para relações curriculares válidas.
- [x] Docentes não qualificados não são elegíveis.
- [x] Indisponibilidades persistidas e adicionais são aplicadas.
- [x] Capacidade e requisitos de sala são transportados para o domínio.
- [x] Dados incompletos produzem diagnóstico explícito.
- [x] Testes provam que não há mistura de cursos/turmas/disciplinas.

## Evidência
- `tests/test_domain.py`: 12 passed.
- `tests/test_cp_sat.py`: passes (legado e domínio integrados).
- Suite completa: 90.76% cobertura.
- Backend: 9 passed, `configure_mappers()` OK, import `app.main` OK.
- `ruff`: `All checks passed!`.

## Estado epistémico
- Implementado: **SIM**
- Testado: **SIM**
- Verificado: **SIM** (execução real + validação independente do domínio)
- Independentemente verificado: **PENDENTE** (T059)

## Fase actual
Plan → Build → Verify → Review (concluído) → Learn.