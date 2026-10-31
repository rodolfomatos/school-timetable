# Shadow Doc SD-BUILD-038 — T051 Fase 3: Modelo de domínio e integração

## Proveniência
Fase 3 do plano de auditoria AES T047–T059, concluída em 31/10/2026 sobre o
commit `f38ff7b` (T050 incluído).

## Objetivo
Introduzir uma camada de domínio canónica, independente do ORM, que traduz os
dados institucionais num ``ProblemInstance`` explícito, eliminando o produto
cartesiano implícito e ligando qualificações, currículo e indisponibilidades.

## Decisões tomadas
- Nova camada `src/timetable/domain.py` com `construir_problema()`:
  - Valida turma/disciplina/docente/sala antes de criar sessões.
  - Diagnósticos explícitos: ``ERROR`` impede execução; ``WARNING`` avisa.
  - Subtrai indisponibilidades persistidas + adicionais da disponibilidade.
  - ``Professor.qualificacoes_definidas`` distingue legado de "sem
    qualificação declarada".
- ``SessaoRequerida`` com ``lesson_id`` estável, ``professores_elegiveis``,
  ``subgrupo_id`` preservado.
- CP-SAT usa ``ctx.sessoes_requeridas`` quando presente; variáveis só para
  elegíveis da sessão (não produto cartesiano).
- ORM: tabelas de associação ``class_subjects`` (currículo) e
  ``teacher_subjects`` (qualificações) com chaves únicas compostas.
- Não houve alteração de contrato público da API — o backend adapta ORM→DTO.

## Evidência
- ``tests/test_domain.py``: 12 testes cobrindo todos os códigos de diagnóstico.
- ``tests/test_cp_sat.py``: passes (legado e domínio integrados).
- Suite completa: 90.76% cobertura.
- Backend: 9 passed, ``configure_mappers()`` OK, ``from app.main import app`` OK.
- ``ruff``: ``All checks passed!``.

## Escore epistémico
Alta confiança — cada regra de domínio tem teste, o solver passa a receber
sessões explícitas e qualificações, e os diagnósticos tornam falhas de dados
visíveis antes da execução do solver.

## Próximos passos
- T052: seed e validador (construção de solução inicial válida, tri-state
  disponibilidade).