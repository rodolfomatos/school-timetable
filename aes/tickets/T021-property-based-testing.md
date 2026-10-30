# Ticket T021 — Property-based Testing para Restrições Duras

## Contexto
Testes unitários tradicionais cobrem casos específicos, mas não garantem que as restrições duras sejam respeitadas em todos os casos possíveis. Property-based testing (com Hypothesis) gera entradas aleatórias e verifica que propriedades são sempre satisfeitas.

## Objetivo
Implementar testes baseados em propriedades para:
1. Verificar que `verificar_hard` nunca retorna violações para horários gerados pelo solver (quando viável)
2. Verificar que `mover_aula` e `trocar_aulas` respeitam slots imutáveis
3. Verificar que a função objetivo nunca retorna score melhor para horários com violações duras

## Critérios de Aceitação
1. `tests/test_property_based.py` implementado com Hypothesis
2. Pelo menos 3 propriedades testadas
3. `make test` passa, `make lint` passa
4. Hypothesis adicionado às dependências de desenvolvimento

## Fase atual
Plan → Build.
