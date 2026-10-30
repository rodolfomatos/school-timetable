# Ticket T018 — Validação com Dados Reais de Escola

## Contexto
O projeto foi desenvolvido com dados sintéticos pequenos (sample_school.json). Para validar escala e performance, é necessário testar com dados reais de uma escola: dezenas de turmas, professores, disciplinas e salas.

## Objetivo
1. Criar um dataset realista de escola média (ex: 10 turmas, 15 professores, 12 disciplinas, 8 salas, 5 dias × 8 horas = 40 slots/semana)
2. Executar o solver (CP-SAT e metaheurísticas) com esses dados
3. Medir tempo de execução, qualidade da solução (score, violações duras, penalidades moles)
4. Documentar gargalos de performance e limitações

## Critérios de Aceitação
1. Dataset realista criado em `data/real_school.json`
2. Teste de integração que executa CP-SAT e metaheurísticas com o dataset real
3. Medição de tempo de execução registada em `aes/metrics/T018-performance.log`
4. Nenhuma restrição dura violada na solução de saída (quando viável)
5. `make test` passa, `make lint` passa

## Riscos (Hostile Analysis)
- Dataset real pode ser muito grande para CP-SAT exato → mitigação: usar metaheurísticas como principal, CP-SAT apenas para validação de viabilidade em subconjuntos
- Performance pode ser lenta com muitas aulas → mitigação: limitar tempo de execução, usar cache de avaliação
- Qualidade da solução pode não ser boa o suficiente → mitigação: ajustar parâmetros (temperatura, tamanho tabu, iterações)

## Fase atual
Plan → Build.
