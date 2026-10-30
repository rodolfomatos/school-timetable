# Shadow Doc SD-BUILD-002 — Linha de base exata CP-SAT (T004)

## Proveniência
Build phase do ticket T004, concluída em 2026-10-29.

## O que foi construído
Implementação completa de `CPSATSolver` em `src/timetable/cp_sat_baseline.py`:

- **Variáveis booleanas** `x[turma, disciplina, professor, sala, slot]` para cada atribuição possível
- **Restrições duras** modeladas como constraints do CP-SAT:
  - H01: professor não dá duas aulas no mesmo slot
  - H02: sala não alberga duas aulas no mesmo slot
  - H03: turma não tem duas aulas no mesmo slot
  - H04: sala compatível com a disciplina
  - H05: professor disponível no slot
  - H07: professores casados não na mesma turma
  - H08: filho não na turma dos pais casados
- **Restrição de cobertura**: cada (turma, disciplina) tem exatamente `carga_semanal` aulas
- **Função objetivo aditiva**: minimiza soma de penalidades moles (S01, S02, S08, S09, S10)
- **Fallback graceful**: se `ortools` não estiver instalado, devolve cópia do horário inicial
- **Geração de slots**: extrai das disponibilidades dos professores, ou usa padrão (seg-sexa, 8h-17h)

## Testes
32 testes no total (incluindo 8 específicos de CP-SAT), 1 skipped (quando ortools não disponível).
Cobertura do ficheiro cp_sat_baseline.py: 89%.

## Decisões de design
1. Variáveis booleanas em vez de variáveis inteiras para simplificar a modelação.
2. Função objetivo aditiva (soma de penalidades), nunca produto multiplicativo.
3. Fallback quando ortools não disponível para manter o projeto executável em qualquer ambiente.
4. 8 workers paralelos no solver CP-SAT.

## Escore epistémico
Alta confiança na modelação das restrições duras (baseada na literatura de CP para timetabling). Média confiança na modelação das restrições moles como penalidades no CP-SAT (abordagem padrão, mas não testada com dados reais de escola).

## Próximos passos
- T005: Refinar Tabu Search / Simulated Annealing em `local_search.py`
- T007: Interface de ajustamento manual
