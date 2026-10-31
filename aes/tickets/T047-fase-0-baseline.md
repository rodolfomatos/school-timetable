# Ticket T047 — Fase 0: Baseline e verificação independente

## Contexto
Iniciar o ciclo de auditoria com um baseline reproduzível. Nenhuma correcção funcional começa antes deste ticket produzir o relatório de evidência.

## Objetivo
Estabelecer o estado real do repositório e reproduzir os findings listados no plano de auditoria (T047–T059).

## Critérios de Aceitação
[ ] Commit e ambiente identificados.
[ ] Comandos de teste documentados e executados ou explicitamente marcados como bloqueados por dependência.
[ ] Cada finding tem severidade, evidência, ficheiro/linha, reprodução e impacto.
[ ] Findings não reproduzidos marcados UNCONFIRMED, não como bugs confirmados.
[ ] T038–T046 reavaliados contra o código e testes.
[ ] Nenhum código funcional alterado nesta fase.
[ ] Relatório produzido em docs/audit/T047-baseline.md e docs/audit/T047-findings.md.

## Fase atual
Plan → Build → Verify.
