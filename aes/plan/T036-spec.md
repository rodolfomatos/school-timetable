# AES Plan Spec — T036 Fase 0: Baseline e Inventário

## 1. Sumário Executivo
Executar a Fase 0 do plano de auditoria: inventário completo do repositório, execução de testes, lint, E2E (se possível), e produção do baseline.md. Nenhuma alteração de código nesta fase.

## 2. Tarefas
- [ ] Registrar commit atual, versão Python/Node, dependências
- [ ] Executar `make test` e registrar cobertura
- [ ] Executar `make lint` e registrar resultados
- [ ] Executar testes E2E Playwright se ambiente permitir
- [ ] Criar docs/audit/baseline.md com módulos, responsabilidades, dependências e cobertura
- [ ] Listar falhas preexistentes separadamente

## 3. Critérios de Aceitação
- docs/audit/baseline.md existe e está completo
- Nenhum código fonte alterado
- Resultados de teste/lint/E2E documentados

## Fase atual
Plan → Build → Verify.
