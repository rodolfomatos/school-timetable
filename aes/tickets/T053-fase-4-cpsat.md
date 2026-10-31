# Ticket T053 — Fase 4: Correção matemática do CP-SAT

## Contexto
CP-SAT usa chave sem lesson_session_id (variáveis sobrescritas); qualquer professor leciona qualquer disciplina; S03, S04, S06, S07 não implementadas; S05 é A-B-A em vez de A-B-C-A.

## Objetivo
Corrigir a modelação CP-SAT para que cada sessão tenha identidade única, qualificações docentes sejam respeitadas, e restrições moles estejam correctamente implementadas e alinhadas com o avaliador Python.

## Critérios de Aceitação
[ ] Carga semanal N produz exactamente N sessões distintas.
[ ] Docente/sala não elegível nunca é seleccionado.
[ ] Conflitos de intervalos parcialmente sobrepostos são detectados.
[ ] LOCKED nunca muda; PREFERRED pode mudar com penalização; FREE sem compromisso.
[ ] Estado OR-Tools é mapeado sem ambiguidade para o contrato de resultado.
[ ] Toda a solução CP-SAT passa no validador independente.
[ ] Testes incluem solução viável, inviável, timeout com incumbent e solver indisponível.

## Fase atual
Plan → Build → Verify.
