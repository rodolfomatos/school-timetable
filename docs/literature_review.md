# Revisão da Literatura — Horário Escolar (School Timetabling)

## Complexidade
O problema é classificado como **NP-hard**; na sua variante de decisão, é NP-completo (redução direta da coloração de grafos; Even et al., 1976; Garey & Johnson, 1979). Não existe uma única classe de problema que corresponda a todos os casos de horário escolar: variam consoante restrições de salas, turmas divididas em sub-grupos, horário semanal vs. outro, etc.

## Consenso Empírico (Competições Internacionais)
As competências ITC-2002, ITC-2003 e ITC-2007 são as referências do domínio. O vencedor de duas das três pistas do ITC-2007 foi um *solver* baseado em programação por restrições (CPSolver). Metaheurísticas de busca local (Tabu Search, Simulated Annealing, Late Acceptance) bateram claramente algoritmos genéticos puros.

Wilke & Ostler (2008) compararam Tabu Search, Simulated Annealing, GA e Branch & Bound nas mesmas condições: **Simulated Annealing apresentou o melhor tradeoff entre tempo de execução e qualidade**. O GA melhorou ao longo de 2 horas, mas com custo muito maior.

## Algoritmo Genético (trabalho acadêmico citado)
- Toda a tabela é um "organismo".
- Tabelas ilegais (dois professores na mesma sala ao mesmo tempo, etc.) são letais e substituídas imediatamente.
- Mutações de "troca" (exchange) são mais comuns que "modificação" (modify).
- Função objetivo era um produto multiplicativo de centenas de pesos → números astronómicos (necessitou `gmp`) → ineficiente. **Lição: usar soma aditiva, não produto.**
- População pequena (100) durante muito tempo vs. grande (10k+) durante poucas gerações: qualidade similar.

## Estratégias de Definição do Problema (recomendadas na literatura)
1. Definir e ranquear todas as restrições conhecidas.
2. Reduzir o espaço de busca com restrições adicionais artificiais (ex. não dar matemática à segunda-feira).
3. Fornecer um horário parcial inicial (~30% dos slots), totalmente viável e imutável (seed).
4. Garantir que algumas restrições são rapidamente computáveis (modelo de dados adequado).
5. Permitir que algumas restrições moles sejam quebradas nos nós finais do grafo; um humano completa o puzzle.

## Restrições do Mundo Real (difíceis de especificar)
- Professor leciona noutro instituto: precisa de tempo de deslocamento entre instituições.
- Professores casados: não devem dar aula na mesma turma.
- Filhos de professores casados: não devem estar na turma dos pais.
- Instalações separadas: turma num instituto um dia, noutro noutro dia.
- Laboratórios partilhados: disponíveis apenas em certos dias da semana.
- Preferências de dia de folga dos professores (segunda, sexta, quarta).
- Preferências manhã/tarde.
- Evitar padrão A-B-C-A (mesma disciplina interrompida).
- Espalhar disciplinas pela semana.
- Duas horas consecutivas para avaliação.

## O verdadeiro desafio: julgar a qualidade, não apenas gerar combinações
Gerar todas as combinações é conceitualmente simples (embora produza volumes grandes de dados). O problema real é julgar se uma solução viável é boa, má ou melhor que outra. Isto envolve fatores humanos difíceis de quantificar:

- Um professor pode trabalhar 5 dias/semana durante X semanas seguidas (solução viável), mas pode ser sub-ótimo comparado a alternar entre dois professores (cada um uma semana).
- Equilíbrio de carga, rotação, justiça percebida e fadiga são difíceis de codificar em software.
- Conclusão: o objetivo não é a otimalidade (100%), mas sim uma solução **"bom o suficiente"** (satisficing) que respeite todas as restrições duras e minimize violações moles, podendo ser ajustada manualmente por um humano.

Este conceito reforça a importância da interface de ajustamento manual (insets de plástico) e do seed parcial imutável.

## Frameworks Open Source
- **Timefold Solver** (ex-OptaPlanner, Apache 2.0, Java/Kotlin) — sucessor oficial do OptaPlanner; quickstart de School Timetabling disponível.
- **UniTime** — voltado a universidades; interface web; finalista/vencedor do ITC-2007.
- **OR-Tools CP-SAT** (Google) — linha de base exata para instâncias pequenas.

## Papers Chave
| Paper | Ano | Onde | Relevância |
|-------|-----|------|------------|
| Schaerf, *A survey of automated timetabling* | 1999 | Artificial Intelligence Review | Survey clássico; coloração de grafos e CSP |
| Burke & Petrovic, *Recent research directions* | 2002 | European J. Oper. Res. | Metaheurísticas e hiper-heurísticas |
| Abramson, *Constructing school timetables using simulated annealing* | 1991 | Management Science | SA para horários escolares |
| Wilke & Ostler, *Solving the School Time Tabling Problem* | 2008 | PATA'08 | Comparação direta: SA > GA |
| Tan, Goh, Kendall & Sabar, *Survey of optimisation methodologies* | 2021 | Expert Systems with Applications | Survey mais recente para high school |
| Ceschia, Di Gaspero & Schaerf, *Educational timetabling* | 2022 | European J. Oper. Res. | Benchmarks e estado da arte |
| Di Gaspero, McCollum & Schaerf, *ITC-2007 Curriculum CTT* | 2007 | QUB Tech Report | Track 3 da competição internacional |
