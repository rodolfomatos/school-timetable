# AES Plan Spec — T001 Scaffolding

## 1. Sumário Executivo
Scaffolding completo de um gerador de horários escolares em Python, seguindo princípios AES (planeamento rigoroso, separação hard/soft constraints, função objetivo aditiva, busca local como motor principal).

## 2. Modelo de Domínio (Entidades)
- **Slot**: (dia_semana, hora) — unidade de tempo.
- **Sala**: identificador, capacidade, tipo (normal, laboratório), dias disponíveis.
- **Professor**: identificador, nome, disponibilidade por slot, dia de folga preferido, preferências manhã/tarde.
- **Turma**: identificador, ano, número de alunos.
- **Disciplina**: identificador, nome, carga horária semanal, tipo de sala requerida.
- **Aula/Ação**: (turma, disciplina, professor, sala, slot) — atribuição única no horário.
- **Horário**: coleção de aulas.

## 3. Restrições Duras (Hard Constraints)
Devem ser 100% satisfeitas para o horário ser viável.
1. Um professor não dá duas aulas no mesmo slot.
2. Uma sala não alberga duas aulas no mesmo slot.
3. Uma turma não tem duas aulas no mesmo slot.
4. Sala compatível com a disciplina (ex. laboratório para ciências).
5. Professor disponível nesse slot.
6. Tempo de deslocamento entre instituições (se aplicável).
7. Professores casados não na mesma turma.
8. Filho não na turma dos pais casados.

## 4. Restrições Moles (Soft Constraints)
Cada violação adiciona uma penalidade à função objetivo (adiitiva).
1. Dia de folga preferido do professor.
2. Preferência manhã/tarde do professor.
3. Agrupar 2 horas consecutivas da mesma disciplina para a mesma turma.
4. Espalhar disciplinas pela semana (evitar bloco único).
5. Evitar padrão A-B-C-A (mesma disciplina separada por outras).
6. Duas horas consecutivas para avaliação (professores selecionados).
7. Carga horária do professor dentro de limites.

## 5. Função Objetivo
`score = -sum(penalidade_mole_i * peso_i)` para todas as restrições moles violadas.
Restrições duras são modeladas como condições de viabilidade (não entram na pontuação aditiva).
Nunca usar produto multiplicativo de pesos (problema do `gmp`/números astronómicos reportado na literatura).

## 6. Arquitetura de Software
```
src/timetable/
  models.py       # Dataclasses de domínio
  constraints.py  # Verificação hard/soft
  objective.py    # Função objetivo aditiva
  seed.py         # Geração de seed parcial imutável (30%)
  solver.py       # Interface do solver
  cp_sat_baseline.py  # Linha de base exata (OR-Tools)
  local_search.py # Tabu Search / Simulated Annealing
  ui.py           # Ajuste manual (insets de plástico)
```

## 7. Testes
- Unitários: modelos, restrições, objetivo.
- Integração: seed → solver → horário viável.
- Cobertura alvo: ≥ 80%.

## 8. Quality Gates
- `make test` passa.
- `make lint` passa (ruff).
- Cobertura ≥ 80%.
- Nenhum código sem ticket associado.

## 9. Aberto / Não Decidido
- Linguagem de UI (CLI vs TTS vs Web): adiar para T007.
- Biblioteca exata específica (ortools vs python-constraint): decidir em T004.
