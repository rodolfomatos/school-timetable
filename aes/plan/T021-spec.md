# AES Plan Spec — T021 Property-based Testing

## 1. Sumário Executivo
Implementar testes baseados em propriedades (Hypothesis) para validar invariantes críticos do solver.

## 2. Propriedades a Testar
### P1: Slots imutáveis são respeitados
Para qualquer horário e qualquer movimento (mover/trocar), se um slot é imutável, a aula nesse slot nunca muda.

### P2: Nenhuma violação dura introduzida
Para qualquer movimento válido (que respeite slots imutáveis), se o horário inicial não tem violações duras, o resultado também não deve ter (ou pelo menos não piorar).

### P3: Score é consistente
Para dois horários idênticos, a avaliação produz o mesmo score.

## 3. Dependências
- `hypothesis` adicionado a `pyproject.toml` em `[project.optional-dependencies]dev`

## 4. Fase atual
Plan → Build.
