# Catálogo de Restrições

## Restrições Duras (Hard)
Devem ser 100% satisfeitas para o horário ser viável.

| ID | Descrição |
|----|-----------|
| H01 | Um professor não dá duas aulas no mesmo slot. |
| H02 | Uma sala não alberga duas aulas no mesmo slot. |
| H03 | Uma turma não tem duas aulas no mesmo slot. |
| H04 | Sala compatível com a disciplina (ex. laboratório para ciências). |
| H05 | Professor disponível nesse slot. |
| H06 | Tempo de deslocamento entre instituições (se aplicável). |
| H07 | Professores casados não na mesma turma. |
| H08 | Filho não na turma dos pais casados. |

## Restrições Moles (Soft)
Cada violação adiciona uma penalidade à função objetivo.

| ID | Descrição | Peso sugerido |
|----|-----------|---------------|
| S01 | Dia de folga preferido do professor não respeitado. | 10 |
| S02 | Preferência manhã/tarde do professor não respeitada. | 8 |
| S03 | Duas horas consecutivas da mesma disciplina não agrupadas. | 6 |
| S04 | Disciplinas não espalhadas pela semana (bloco único). | 5 |
| S05 | Padrão A-B-C-A (mesma disciplina interrompida). | 7 |
| S06 | Falta de duas horas consecutivas para avaliação. | 9 |
| S07 | Carga horária do professor fora dos limites. | 8 |
| S08 | Professor a trabalhar muitas semanas seguidas sem pausa (falta de equilíbrio de carga ao longo do tempo). | 12 |
| S09 | Distribuição desigual de aulas entre professores da mesma disciplina (falta de rotação/alternância). | 11 |
| S10 | Professor com carga concentrada em poucos dias (ex. 5 dias seguidos) em vez de espalhada. | 10 |

## Função Objetivo
```
score = - Σ (penalidade_mole_i × peso_i)
```
Quanto maior (menos negativo), melhor. Restrições duras não entram na pontuação: ou são satisfeitas, ou a solução é inviável.

## Satisficing ("bom o suficiente")
Este problema envolve fatores humanos (preferências, equilíbrio, carga ao longo do tempo) que são difíceis de quantificar exatamente. Por isso, o objetivo não é encontrar a solução ótima (100%), mas sim uma solução **"bom o suficiente"** (satisficing) que respeite todas as restrições duras e minimize as violações moles dentro de um tempo de execução razoável. O utilizador humano deve poder ajustar manualmente o resultado final.
