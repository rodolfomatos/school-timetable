# Shadow Doc SD-BUILD-034 — T059 Fase 8: Verificação epistemológica do AES

## Proveniência
Fase 8 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Impedir que o AES declare trabalho concluído sem evidência verificável e manter alinhados código, testes, tickets, matriz de restrições e shadow documents.

## Decisões tomadas
- Definir estados de evidência IMPLEMENTED, TESTED, VERIFIED, INDEPENDENTLY_VERIFIED.
- Cada ticket deve declarar critérios de aceitação testáveis.
- Cada critério deve apontar para teste, comando, artefacto/log ou revisão independente.
- A conclusão de um ticket exige evidência; ausência de evidência mantém ticket aberto ou parcialmente verificado.
- A matriz de restrições deve ser derivada/reconciliada com o código e os testes, não actualizada apenas manualmente.
- Detectar tickets marcados concluídos sem testes associados ou sem prova de execução.
- Detectar shadow documents desactualizados face ao código.
- Guardar data, commit, ambiente e agente/verificador da evidência.
- Não permitir que o mesmo artefacto de implementação seja a única prova da sua própria correcção.

## Escore epistémico
Alta confiança — baseada na filosofia de engenharia de software e na governança epistémica do AES.

## Próximos passos
- Executar T047–T058 e aplicar T059 como gate final de cada ticket.
