# Shadow Doc SD-BUILD-006 — Restrições Moles S04-S07 (T014)

## Proveniência
Build phase do ticket T014, concluída em 2026-10-29. Corrigi F-003 (MAJOR).

## Restrições Moles Implementadas

| ID | Descrição | Peso | Implementação |
|----|-----------|------|---------------|
| S04 | Disciplinas não espalhadas pela semana (todas as aulas num único dia) | 5 | Agrupa aulas por (turma, disciplina, dia); se todas as aulas de uma (turma, disciplina) estão num único dia e há >= 2 aulas, penaliza |
| S05 | Padrão A-B-C-A (mesma disciplina interrompida por outra no mesmo dia) | 7 | Ordena aulas por (turma, dia, hora); verifica sequências disc[i]==disc[i+2]!=disc[i+1] |
| S06 | Falta de duas horas consecutivas para avaliação | 9 | Para professores com carga_maxima >= 4, verifica se há pelo menos um bloco de 2h consecutivas por dia |
| S07 | Carga horária do professor fora dos limites | 8 | Compara total de aulas por professor com [carga_minima_semanal, carga_maxima_semanal] |

## Testes adicionados (8 novos)
- test_s04_todas_aulas_num_unico_dia
- test_s04_aulas_espalhadas_sem_penalidade
- test_s05_padrao_interrompido
- test_s05_sem_padrao_interrompido
- test_s06_sem_bloco_consecutivo
- test_s06_com_bloco_consecutivo
- test_s07_carga_abaixo_minimo
- test_s07_carga_acima_maximo
- test_s07_carga_dentro_limites

## Cobertura
- `constraints.py`: 94% (era 89%)
- Total do projeto: 91.44%

## Escore epistémico
Alta confiança: cada restrição é diretamente mapeada do catálogo em `docs/constraints.md` para código testável.

## Próximos passos
- T015: Corrigir CP-SAT S09/S10 (F-004, F-005, MAJOR)
- T016: Avaliação incremental (F-006, MAJOR)
- T017: Findings MINOR (F-007 a F-011)
