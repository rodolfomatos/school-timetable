# Ticket T007 — Interface de Ajuste Manual ("Insets de Plástico")

## Contexto
Na prática real, o horário nunca sai 100% automático. Um humano precisa ajustar o resultado final, quebrando eventualmente uma regra menor com informação contextual não disponível ao algoritmo (ex. "matemática à tarde só para a turma avançada"). A UI deve permitir ao usuário visualizar e editar o horário como uma tabela com "insets de plástico" movíveis.

## Objetivo
Implementar `src/timetable/ui.py` com:
1. Exportação/importação de horários para JSON (esqueleto já existe, precisa ser expandido)
2. Representação de horário como grade (turmas × slots) para visualização
3. Funções de movimento manual de aulas entre slots (trocar, mover, remover)
4. Validação de restrições duras após cada movimento manual
5. Registro de quais slots são imutáveis (seed) vs. mutáveis

## Critérios de Aceitação
1. `make test` passa (incluindo novos testes de UI).
2. `make lint` passa sem erros.
3. A UI consegue serializar um horário para JSON e deserializar de volta com integridade.
4. Movimento manual de aula entre slots é possível e atualiza o horário.
5. Slots imutáveis são respeitados (não podem ser alterados pela UI manual).
6. Após movimento manual, as restrições duras podem ser verificadas com `verificar_hard`.

## Riscos (Hostile Analysis)
- Usuário cria violações de restrições duras ao mover manualmente → mitigação: fornecer função de validação pós-movimento.
- Dados corrompidos na importação JSON → mitigação: validação de estrutura ao importar.
- Escopo de UI (CLI vs Web vs TUI) → mitigação: manter como biblioteca de funções, sem framework de UI específico nesta fase.

## Estado
**Concluído** (Plan → Build → Verify)

## Critérios de Aceitação — Status
1. `make test` passa (57 testes, incluindo UI de ajuste manual). — **OK**
2. `make lint` passa sem erros. — **OK**
3. A UI consegue serializar um horário para JSON e deserializar de volta com integridade. — **OK** (test_exportar_importar_json_integridade)
4. Movimento manual de aula entre slots é possível e atualiza o horário. — **OK** (test_mover_aula_mutavel_funciona)
5. Slots imutáveis são respeitados (não podem ser alterados pela UI manual). — **OK** (testes de mover/trocar/remover com slots imutáveis)
6. Após movimento manual, as restrições duras podem ser verificadas com `verificar_hard`. — **OK** (test_validar_apos_movimento_sem_violacoes)

## Fase atual
Concluído. Próximo: T009 (Revisão hostil / peer review).
