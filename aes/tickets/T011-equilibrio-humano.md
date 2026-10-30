# Ticket T011 — Restrições de Equilíbrio Humano (S08-S10) + Satisficing

## Contexto
Comentário adicional do utilizador: o verdadeiro desafio do horário escolar não é gerar combinações, mas julgar a qualidade de soluções viáveis. Fatores humanos (carga ao longo do tempo, rotação entre professores, justiça percebida) são difíceis de codificar. O objetivo não é a otimalidade (100%), mas sim "bom o suficiente" (satisficing).

## Objetivo
Adicionar restrições moles de equilíbrio humano ao modelo e documentar o conceito de satisficing.

## Restrições Moles Adicionadas
| ID | Descrição | Peso |
|----|-----------|------|
| S08 | Professor a trabalhar muitos dias seguidos sem pausa | 12 |
| S09 | Distribuição desigual de aulas entre professores da mesma disciplina | 11 |
| S10 | Carga concentrada em poucos dias para o mesmo professor | 10 |

## Arquivo alterado
- `docs/constraints.md` — catálogo atualizado com S08-S10 + secção "Satisficing"
- `src/timetable/constraints.py` — implementação de S08, S09, S10
- `aes/shadow/SD-LEARN-001.md` — shadow doc capturando as ideias do comentário
- `docs/literature_review.md` — secção sobre julgamento de qualidade e satisficing

## Critérios de Aceitação
1. `make test` passa com as novas restrições.
2. `make lint` passa sem erros.
3. S08, S09, S10 aparecem no catálogo de restrições.
4. Shadow doc SD-LEARN-001 existe e documenta satisficing.

## Fase atual
Plan → Build → Verify (concluído).
