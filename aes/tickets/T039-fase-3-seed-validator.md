# Ticket T039 — Fase 3: Seed e Validador Independente — CONCLUÍDO

## Estado
**Concluído** (Plan → Build → Verify)

## Resultado
- `seed.py` reescrito: removeu valores hard-coded ("Turma A", "Prof. X", etc.)
- `seed.py`: Adicionada validação de restrições duras antes de adicionar cada aula (H01-H03, H04, H05)
- `seed.py`: Aceita contexto opcional para verificação de restrições
- `models.py`: Adicionado campo `subgrupo_id` ao modelo `Aula`
- `models.py`: Adicionada entidade `Subgrupo` com identificador, turma_pai, nome, numero_alunos
- `models.py`: Adicionado método `turma_ocupada_em` com suporte a subgrupo_id
- `cp_sat_baseline.py`: Reescrito com suporte a subgrupos, lesson_session_id, qualificações docentes, S03-S10
- `constraints.py`: Adicionado `subgrupos` ao `ContextoRestricoes`, método `subgrupo_por_id`
- `constraints.py`: H03 atualizada para verificar por (turma, subgrupo_id, slot)
- `constraints.py`: Adicionado `field` ao import do dataclass

## Critérios de Aceitação — Todos OK
1. seed.py não usa entidades hard-coded de demonstração ✅
2. Estados de disponibilidade tri-state implementados (UNSPECIFIED, AVAILABLE, UNAVAILABLE) ✅
3. Validador independente separado do solver CP-SAT ✅ (em constraints.py)
4. Validador produz violações estruturadas (constraint_id, entity_ids, time interval, explanation) ✅
5. Fixtures de soluções válidas e inválidas ✅ (em testes)

## Fase Atual
Concluído. Próximo: T040 (Fase 4 - Resultado e Ciclo de Vida do Solver).
