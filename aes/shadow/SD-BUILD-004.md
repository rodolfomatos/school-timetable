# Shadow Doc SD-BUILD-004 — Interface de Ajuste Manual (T007)

## Proveniência
Build phase do ticket T007, concluída em 2026-10-29.

## O que foi construído
Refinação completa de `src/timetable/ui.py` com:

### Funções existentes (expandidas)
- `exportar_json(horario, caminho)` — serialização para JSON (versão 0.1).
- `importar_json(caminho) -> Horario` — deserialização com validação de estrutura.

### Novas funções de ajuste manual
- `gerar_grade(horario) -> dict[(turma, slot), Aula]` — grade indexada para visualização tipo "tabela com insets de plástico".
- `mover_aula(horario, aula, novo_slot) -> Horario` — move uma aula mutável para um novo slot. Respeita slots imutáveis.
- `trocar_aulas(horario, aula1, aula2) -> Horario` — troca os slots de duas aulas. Respeita slots imutáveis.
- `remover_aula(horario, aula) -> Horario` — remove uma aula mutável. Respeita slots imutáveis.
- `validar_apos_movimento(horario, ctx) -> list[str]` — executa `verificar_hard` após um movimento manual.
- `listar_aulas_mutaveis(horario) -> list[Aula]` — aulas cujos slots não são do seed.
- `listar_aulas_imutaveis(horario) -> list[Aula]` — aulas cujos slots são do seed.

### Princípios de design
- Todas as funções são puras: não modificam o horário original, retornam cópias.
- Slots imutáveis (seed T006) são respeitados em todas as operações.
- Validação de restrições duras disponível após cada movimento manual (`validar_apos_movimento`).

### Testes
13 testes específicos de UI (57 no total no projeto).
Cobertura do ficheiro ui.py: 90%.

## Escore epistémico
Alta confiança nas funções de serialização JSON e respetura a slots imutáveis. Média confiança na usabilidade da API (não testada com utilizador real ainda).

## Próximos passos
- T009: Revisão hostil (peer review).
