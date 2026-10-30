# Quality Gates (AES)

## Gate de Entrada (Plan → Build)
- [ ] Ticket criado com título, contexto, objetivo e ACs.
- [ ] Spec aprovada (arquitetura, modelo de domínio, restrições).
- [ ] Análise de riscos hostil documentada.

## Gate de Saída (Build → Verify)
- [ ] `make test` passa (cobertura ≥ 80%).
- [ ] `make lint` passa (ruff, sem erros).
- [ ] `make typecheck` passa (mypy strict).
- [ ] Cada ficheiro de código tem ticket associado.

## Gate de Verificação (Verify → Review)
- [ ] Testes unitários cobrem modelos, restrições e objetivo.
- [ ] Teste de integração: seed → solver → horário viável.
- [ ] Nenhuma restrição dura violada na solução de saída.

## Gate de Revisão (Review → Learn)
- [ ] Revisão hostil concluída (senior engineer).
- [ ] Feedback incorporado ou ticket criado para pendências.

## Gate de Aprendizagem (Learn → Fechado)
- [ ] Shadow doc criado com decisões, porquê e escore epistémico.
- [ ] Kanban atualizado.
- [ ] Métricas registadas em `aes/metrics/`.
