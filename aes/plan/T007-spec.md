# AES Plan Spec — T007 Interface de Ajuste Manual

## 1. Sumário Executivo
Implementar funções de UI para ajustamento manual de horários, permitindo ao usuário visualizar e editar o horário como uma grade, com respeito a slots imutáveis e validação de restrições duras.

## 2. Estrutura de Dados para UI
### Grade de Horário
Dicionário: `(turma, slot) -> Aula` para visualização rápida.

### Slots Imutáveis vs. Mutáveis
- Imutáveis: slots do seed (não podem ser alterados pela UI).
- Mutáveis: todos os outros slots.

## 3. Funções da UI
### `gerar_grade(horario) -> dict[tuple[str, Slot], Aula]`
Converte um Horario em uma grade indexada por (turma, slot).

### `mover_aula(horario, aula, novo_slot) -> Horario`
Move uma aula para um novo slot. Retorna um novo Horario. Não altera se o slot for imutável.

### `trocar_aulas(horario, aula1, aula2) -> Horario`
Troca os slots de duas aulas. Retorna um novo Horario. Respeita slots imutáveis.

### `remover_aula(horario, aula) -> Horario`
Remove uma aula do horário. Não remove se o slot for imutável.

### `exportar_json(horario, caminho)` / `importar_json(caminho) -> Horario`
Serialização/deserialização para JSON (expansão do esqueleto existente).

### `validar_apos_movimento(horario, ctx) -> list[str]`
Executa `verificar_hard` e retorna violações.

## 4. Interface
Todas as funções são puras (não modificam o horário original, retornam cópias).

## 5. Testes
- Teste de exportação/importação JSON com integridade.
- Teste de movimento manual respeitando slots imutáveis.
- Teste de troca de aulas respeitando slots imutáveis.
- Teste de validação de restrições duras após movimento.
- Teste de geração de grade.
