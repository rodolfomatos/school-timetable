# AES Plan Spec — T053 Fase 4: Correção matemática do CP-SAT

## 1. Sumário Executivo
Garantir que cada sessão requerida tem identidade única e estável; que cada sessão l tem exatamente uma atribuição admissível; que variáveis são criadas apenas para combinações admissíveis; que restrições duras são modeladas correctamente.

## 2. Objetivo
- Rever variáveis de decisão e garantir chave única por lesson_session_id.
- Para cada sessão requerida l, impor exatamente uma atribuição admissível: sum(x[l,teacher,room,timeslot,...]) == 1.
- Criar variáveis apenas para docentes, salas, grupos e slots elegíveis.
- Modelar conflitos de docente, sala, turma e subgrupo.
- Modelar duração real e sobreposição de intervalos, não apenas igualdade de slot quando a duração pode atravessar slots.
- Aplicar reservas de sala, indisponibilidades, setup/cleanup e regras de calendário.
- Definir semântica de horario_inicial: warm start/hint, atribuições fixas, preferências ou solução de referência. Não assumir que passar o parâmetro significa preservá-lo.
- Implementar LOCKED como restrição hard; PREFERRED como custo de alteração; FREE sem compromisso.
- Não devolver cópia do horário inicial quando OR-Tools não está disponível ou quando não há solução.
- Toda a solução CP-SAT deve passar no validador independente.

## 3. Critérios de Aceitação
[ ] Carga semanal N produz exactamente N sessões distintas.
[ ] Docente/sala não elegível nunca é seleccionado.
[ ] Conflitos de intervalos parcialmente sobrepostos são detectados.
[ ] LOCKED nunca muda; PREFERRED pode mudar com penalização; FREE sem compromisso.
[ ] Estado OR-Tools é mapeado sem ambiguidade para o contrato de resultado.
[ ] Toda a solução CP-SAT passa no validador independente.
[ ] Testes incluem solução viável, inviável, timeout com incumbent e solver indisponível.

## 4. Fase atual
Plan → Build → Verify.
