# AES Plan Spec — T047 Fase 0: Baseline e verificação independente

## 1. Sumário Executivo
Estabelecer uma baseline reproduzível e verificar independentemente o estado real do código, testes, documentação e tickets T036–T046. Nenhuma correcção funcional deve começar antes de este ticket produzir o relatório de evidência.

## 2. Objetivo
Executar a Fase 0 do plano de auditoria (T047–T059):
- Registrar commit, branch, versão Python/Node, sistema operativo e dependências.
- Executar testes Python, lint, type checks, testes de API, ORM, frontend build e E2E, quando disponíveis.
- Reproduzir os findings enumerados no plano de auditoria.
- Comparar declarações dos tickets e documentos AES com o comportamento real.
- Registar comandos, stdout/stderr, exit codes e limitações ambientais.

## 3. Findings a verificar
1. Imports inválidos ou ausentes em routers/dependências.
2. Dependência circular entre main.py e schedules.py via limiter.
3. Configuração de mappers SQLAlchemy e relações back_populates/FK.
4. Registo público permite ou não escolher papel privilegiado.
5. seed.py ainda contém placeholders hard-coded e está marcado como esqueleto.
6. Uso de frozenset seguido de .add() no contexto de disponibilidades.
7. Metaheurísticas iniciadas com Horario() vazio.
8. CP-SAT não utiliza efectivamente o horário inicial/slots bloqueados.
9. Perda de subgrupo_id nos movimentos locais.
10. Discrepâncias S01–S10 entre CP-SAT e avaliador Python.
11. Cache de avaliação não inclui identidade/versão do contexto.
16. Serviço não aplica additional_unavailabilities, qualificações e relações curriculares.
17. Serviço não persiste ScheduleVersion/ScheduleAssignment.
18. Jobs mantidos apenas em memória.
19. Consultas não filtradas por institution_id.
20. create_all usado como mecanismo de evolução do schema.

## 4. Critérios de Aceitação
[ ] Commit e ambiente identificados.
[ ] Comandos de teste documentados e executados ou explicitamente marcados como bloqueados por dependência.
[ ] Cada finding tem severidade, evidência, ficheiro/linha, reprodução e impacto.
[ ] Findings não reproduzidos marcados UNCONFIRMED, não como bugs confirmados.
[ ] T038–T046 reavaliados contra o código e testes.
[ ] Nenhum código funcional alterado nesta fase.
[ ] Relatório produzido em docs/audit/T047-baseline.md e docs/audit/T047-findings.md.

## 5. Fase atual
Plan → Build → Verify.
