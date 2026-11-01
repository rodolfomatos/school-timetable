# Shadow Doc SD-BUILD-040 — T053 Fase 4: Correção matemática do CP-SAT

## Proveniência
Fase 4 do plano de auditoria AES T047–T059, concluída em 01/11/2026 sobre o
commit `db16c31` (T052 incluído).

## Objetivo
Alinhar o modelo CP-SAT ao validador Python independente (restrições moles
S02, S05, S08, S09, S10), eliminando divergências que permitiam soluções
avaliadas diferentemente.

## Decisões tomadas
- **S02**: CP-SAT simplificado para `sl.hora >= 13` (tarde), igual ao Python.
  Removida a chamada a `Slot.eh_manha()` que introduzia assimetria.
- **S05**: Padrão corrigido de A-B-A (3 posições) para A-B-C-A (4 posições:
  disc1, disc2, disc3, disc1 com 4 disciplinas distintas). Implementado
  em ambos: Python (loop simples) e CP-SAT (variáveis booleanas por slot).
- **S08**: CP-SAT alterado de "5 dias consecutivos" para "≥ 5 dias totais
  com aula" (alinhado ao Python). Usa soma de variáveis booleanas por dia.
- **S09**: CP-SAT alterado de normalização por carga média (25%) para
  diferença absoluta `max - min > 2` (alinhado ao Python).
- **S10**: CP-SAT alterado de "≥ 5 aulas num único dia" para
  "≤ 2 dias com aula E ≥ 5 aulas totais" (alinhado ao Python).
- Testes actualizados: S05 testa A-B-C-A; S02/S08/S09/S10 verificam alinhamento.

## Evidência
- Suite completa: 88.31% cobertura.
- Backend: 9 passed, `from app.main import app` OK, `ruff` clean.
- Regressão S05: teste A-B-A passa no código antigo; teste A-B-C-A passa no novo.
- Nenhuma alteração de contrato público da API.

## Escore epistémico
Alta confiança — cada restrição mole tem implementação paralela em Python e
CP-SAT com semântica idêntica, testada independentemente.

## Próximos passos
- T054: semântica dos subgrupos (conflito turma inteira vs subgrupo, cardinalidade
  por subgrupo, preservação `subgrupo_id`).