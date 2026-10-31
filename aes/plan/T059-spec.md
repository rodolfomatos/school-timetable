# AES Plan Spec — T059 Fase 8: Verificação epistemológica do AES

## 1. Sumário Executivo
Impedir que o AES declare trabalho concluído sem evidência verificável e manter alinhados código, testes, tickets, matriz de restrições e shadow documents.

## 2. Objetivo
- Definir estados de evidência IMPLEMENTED, TESTED, VERIFIED, INDEPENDENTLY_VERIFIED.
- Cada ticket deve declarar critérios de aceitação testáveis.
- Cada critério deve apontar para teste, comando, artefacto/log ou revisão independente.
- A conclusão de um ticket exige evidência; ausência de evidência mantém ticket aberto ou parcialmente verificado.
- A matriz de restrições deve ser derivada/reconciliada com o código e os testes, não actualizada apenas manualmente.
- Detectar tickets marcados concluídos sem testes associados ou sem prova de execução.
- Detectar shadow documents desactualizados face ao código.
- Guardar data, commit, ambiente e agente/verificador da evidência.
- Não permitir que o mesmo artefacto de implementação seja a única prova da sua própria correcção.

## 3. Critérios de Aceitação
[ ] Kanban inclui estado de implementação e estado de evidência separados.
[ ] Ticket sem evidência não pode ser marcado VERIFIED.
[ ] Relatório identifica tickets fechados sem testes/evidência.
[ ] Matriz de restrições tem links para implementação e testes.
[ ] Shadow documents indicam commit/versão a que correspondem.
[ ] Existe relatório de divergências código ↔ docs ↔ testes.
[ ] Pelo menos um finding histórico é detectado automaticamente como exemplo.

## 4. Fase atual
Plan → Learn.
