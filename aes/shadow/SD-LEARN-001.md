# Shadow Doc SD-LEARN-001 — Julgamento de Qualidade e Fatores Humanos

## Proveniência
Comentário adicional partilhado pelo utilizador sobre o problema do horário escolar, enfatizando que o verdadeiro desafio não é gerar combinações, mas julgar a qualidade de soluções viáveis.

## Ideias-chave capturadas

### 1. O desafio não é enumerar, é avaliar
Gerar todas as combinações é conceitualmente simples (embora produz volumes grandes de dados). O problema real é: dado um horário viável, como julgar se é bom, mau ou melhor que outro? Isto requer mais do que verificar se é "possível".

### 2. Fatores humanos são difíceis de codificar
Exemplo concreto do comentário: um professor poderia trabalhar 5 dias/semana durante X semanas seguidas (solução viável), mas isso pode ser sub-ótimo comparado a alternar entre dois professores (cada um uma semana). Este tipo de equilíbrio/balanceamento é muito difícil de construir em software porque envolve:
- Preferências subjetivas dos professores
- Carga ao longo do tempo (semanas seguidas vs. rotação)
- Justiça percebida entre profissionais
- Fadiga e bem-estar

### 3. Satisficing ("bom o suficiente")
Como o problema envolve fatores humanos impossíveis de quantificar exatamente, o objetivo não é a otimalidade (100%). É uma solução "bom o suficiente" que:
- Respeita 100% das restrições duras
- Minimiza violações moles
- Pode ser ajustada manualmente por um humano no final

## Impacto no projeto
- Adicionadas restrições moles S08, S09, S10 (equilíbrio de carga, rotação, concentração de dias)
- Função objetivo mantém-se aditiva (soma de penalidades)
- A UI de ajustamento manual (T007) é ainda mais importante: o humano completa o puzzle
- O conceito de "bom o suficiente" deve orientar os critérios de parada do solver

## Escore epistémico
Alta confiança: estas observações vêm da experiência prática reportada e corroboram a literatura (ITC 2007, surveys de Burke/Schaerf/Ceschia).
