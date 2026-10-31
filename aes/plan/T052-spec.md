# AES Plan Spec — T052 Fase 3: Construção de solução inicial

## 1. Sumário Executivo
Garantir que SA e Tabu Search recebem uma solução inicial não vazia, construída a partir das sessões requeridas e validada antes da optimização.

## 2. Objetivo
- Substituir placeholders em src/timetable/seed.py por construção baseada no ProblemInstance.
- Não usar nomes fixos como Turma A, Prof. X, Sala 1 em código de produção.
- Construir solução completa ou declarar explicitamente que apenas foi possível obter solução parcial.
- Usar CP-SAT como construtor de solução inicial quando disponível; caso contrário, implementar construtor heurístico com validação e backtracking/repair.
- Não interpretar Horario() vazio como solução válida de um problema com sessões obrigatórias.
- Distinguir LOCKED, PREFERRED e FREE; seed parcial não significa automaticamente slots imutáveis.
- Garantir reprodutibilidade por random seed.
- Não mutar o estado global do gerador aleatório; usar instância random.Random.

## 3. Critérios de Aceitação
[ ] Problema com sessões obrigatórias não pode produzir sucesso com horário vazio.
[ ] Número de sessões atribuídas corresponde ao número requerido, salvo estado parcial explícito.
[ ] Seed passa pelo validador independente.
[ ] Seed é reprodutível para a mesma instância e random seed.
[ ] Seed não contém entidades fora do ProblemInstance.
[ ] SA/Tabu recusam input inviável ou vazio, salvo modo explicitamente permitido.
[ ] Testes cobrem problema viável, inviável e parcialmente preenchível.

## 4. Fase atual
Plan → Build → Verify.
