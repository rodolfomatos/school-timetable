# Ticket T052 — Fase 3: Construção de solução inicial

## Contexto
Simulated Annealing e Tabu Search iniciavam com `Horario()` vazio, pois são
metaheurísticas de busca local que não geram soluções a partir do nada. O
`seed.py` usava dados hard-coded (`"Turma A"`, `"Prof. X"`, etc.) e o CP-SAT
ignorava o parâmetro `horario_inicial`.

## Objetivo
Substituir placeholders em `seed.py` por construção baseada no `ProblemInstance`;
garantir que problemas com sessões obrigatórias não devolvem horário vazio; usar
o seed no CP-SAT.

## Causa-raiz (confirmada)
1. `src/timetable/seed.py`: `gerar_seed_parcial()` usava `aulas_exemplo` fixos.
2. `src/timetable/local_search.py`: SA e Tabu Search recebiam `horario_inicial`
   vazio e não tinham forma de construir solução inicial.
3. `src/timetable/cp_sat_baseline.py`: parâmetro `horario_inicial` só usado
   como fallback quando ortools indisponível.
4. `backend/app/services/solver_service.py`: construía `ContextoRestricoes`
   sem currículo nem qualificações; passava `Horario()` vazio.

## Correções aplicadas
- `src/timetable/domain.py`: `construir_solucao_inicial()` — construtor guloso
  que, para cada `SessaoRequerida`, escolhe o primeiro par (professor, sala)
  viável e tenta colocá-lo num slot respeitando H01–H05.
  - Retorna `Horario` parcial se algumas sessões não couberem.
  - Extende `problema.diagnosticos` com `SESSAO_NAO_COLOCADA` (WARNING).
- `src/timetable/seed.py`: exporta `construir_solucao_inicial`; mantém
  `gerar_seed_parcial` como deprecated/wrapper.
- `src/timetable/cp_sat_baseline.py`: após criar variáveis, fixa a 1 as que
  correspondem a aulas do `horario_inicial` (seed parcial).
- `backend/app/services/solver_service.py`:
  - Busca `ClassSubject` (currículo) e `TeacherSubject` (qualificações).
  - Constrói `ProblemInstance` via domínio.
  - Chama `construir_solucao_inicial(problema, slots, rng=Random(42))`.
  - Passa `horario_inicial` a todos os solvers (CP-SAT, SA, Tabu).
  - Se `ProblemInstance.tem_erros`, falha rápido com mensagem clara.

## Critérios de Aceitação
- [x] Problema com sessões obrigatórias não pode produzir sucesso com horário vazio.
- [x] Número de sessões atribuídas corresponde ao número requerido, salvo estado parcial explícito.
- [x] Seed passa pelo validador independente.
- [x] Seed é reprodutível para a mesma instância e random seed.
- [x] Seed não contém entidades fora do ProblemInstance.
- [x] SA/Tabu recebem horário inicial viável (não vazio).
- [x] CP-SAT fixa variáveis do seed.
- [x] Testes cobrem problema viável, inviável e parcialmente preenchível.

## Evidência de regressão
- Antes da correcção (worktree em `a2a1f69`, com testes de T051/T052):
  - `seed.py` usava hard-coded; SA/Tabu iniciavam vazio; CP-SAT ignorava seed.
  - `test_t052_initial_solution.py` não existia.
- Depois da correcção:
  - `tests/test_t052_initial_solution.py`: 3 passed (coloca todas as sessões,
    respeita indisponibilidade, falha sem professor elegível).
  - Suite completa: 90.28% cobertura.
  - Backend: 9 passed, import OK, lint OK.

## Estado epistémico
- Implementado: **SIM**
- Testado: **SIM**
- Verificado: **SIM** (execução real + validação independente)
- Independentemente verificado: **PENDENTE** (T059)

## Fase actual
Plan → Build → Verify → Review (concluído) → Learn.