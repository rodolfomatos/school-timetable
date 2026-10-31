# AES Plan Spec — T055 Fase 5: Consistencia das restrições S01–S10

## 1. Sumário Executivo
Definir formalmente S01–S10 e garantir que o avaliador Python e CP-SAT implementam a mesma semântica.

## 2. Objetivo
Para cada restrição documentar:
- Definição matemática.
- Entidades e janela temporal abrangidas.
- Unidade da penalização.
- Limites e parâmetros configuráveis.
- Casos de fronteira.
- Se é preferência, objectivo ou requisito hard.

Rever especificamente:
- S02: usar início/fim do TimeSlot, não índice de hora arbitrário.
- S03/S06: definir se penaliza ausência de bloco, número de blocos ou pares adjacentes; evitar multiplicação acidental de penalizações.
- S04: criar indicadores por dia/disciplina, não duplicados por slot.
- S05: alinhar especificação/documentação A-B-C-A com implementação; não aceitar implementação A-B-A como equivalente.
- S07: se é soft, a variável de carga não pode ter domínio que torne a violação impossível; usar variável de excesso/reificação correcta.
- S08: equivalência lógica completa das variáveis reificadas; ordem cronológica dos dias; definir dias consecutivos.
- S09: normalizar por carga contratual/expectativa aplicável.
- S10: mesma condição e limiar em ambos os motores.

## 3. Critérios de Aceitação
[ ] Todas as regras têm especificação formal aprovada.
[ ] Testes unitários cobrem fronteiras e contra-exemplos.
[ ] CP-SAT e Python concordam sobre a penalização em instâncias de teste controladas.
[ ] Reificações são bidireccionais quando necessário.
[ ] A matriz de restrições reflecte o estado real.
[ ] Nenhuma regra soft é acidentalmente transformada em hard.

## 4. Fase atual
Plan → Build → Verify.
