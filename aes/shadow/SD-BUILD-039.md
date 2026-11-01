# Shadow Doc SD-BUILD-039 — T052 Fase 3: Construção de solução inicial

## Proveniência
Fase 3 do plano de auditoria AES T047–T059, concluída em 01/11/2026 sobre o
commit `a2a1f69` (T051 incluído).

## Objetivo
Garantir que todos os solvers (CP-SAT, SA, Tabu) recebam uma solução inicial
viável, construída a partir do `ProblemInstance`, eliminando o horário vazio e
os dados hard-coded do `seed.py`.

## Decisões tomadas
- `construir_solucao_inicial()` em `seed.py`: construtor guloso determinístico
  (seed fixo 42). Para cada sessão, itera sobre pares (professor, sala) válidos
  e tenta colocar no primeiro slot livre. Não é busca local — apenas construção
  inicial viável.
- Diagnóstico `SESSAO_NAO_COLOCADA` (WARNING) quando a sessão não couber;
  mantém o problema executável e reporta o que ficou de fora.
- CP-SAT fixa variáveis correspondentes ao seed: para cada aula do
  `horario_inicial`, encontra a variável `(lesson_id, prof, sala, slot, sub)`
  e adiciona `model.Add(var == 1)`. SA e Tabu recebem o seed e operam sobre ele.
- Backend adapta ORM→DTO: busca `ClassSubject` e `TeacherSubject`, constrói
  `ProblemInstance`, valida (falha rápido se `tem_erros`), depois constrói
  solução inicial.
- Não houve alteração de contrato público da API.

## Evidência
- `tests/test_t052_initial_solution.py`: 3 passed (coloca todas as sessões,
  respeita indisponibilidade, falha sem professor elegível).
- Suite completa: 90.28% cobertura.
- Backend: 9 passed, `from app.main import app` OK, `ruff` clean.

## Escore epistémico
Alta confiança — cada regra de domínio tem teste, o solver passa a receber
seed viável, e os diagnósticos tornam falhas de dados visíveis antes da
execução do solver.

## Próximos passos
- T053: correção matemática do CP-SAT (S02/S05/S08/S09/S10, usar
  `horario_inicial` completo, `slots_imutaveis`).