# Shadow Doc SD-BUILD-017 — Fase 3: Seed e Validador Independente (T039)

## Proveniência
Fase 3 do plano de auditoria (DOCX seção 11), concluída em 31/10/2026.

## O que foi construído

### seed.py reescrito
- Removidos valores hard-coded ("Turma A", "Prof. X", "Sala 1", etc.)
- Adicionada validação de restrições duras (H01-H05) antes de adicionar cada aula
- Adicionado parâmetro opcional `ctx` (ContextoRestricoes) para validação
- Cada aula do seed é verificada contra restrições duras antes de ser adicionada

### Modelo de domínio atualizado (models.py)
- `Aula`: campo opcional `subgrupo_id: Optional[str] = None`
- `Subgrupo`: nova entidade com identificador, turma_pai, nome, numero_alunos
- `Horario.turma_ocupada_em`: agora aceita parâmetro opcional `subgrupo_id`
- Duas aulas da mesma turma podem ocorrer no mesmo slot se forem de subgrupos diferentes

### CP-SAT atualizado (cp_sat_baseline.py)
- Reescrito com suporte a subgrupos (variáveis incluem subgrupo_id)
- lesson_session_id como identidade única para cada sessão
- Qualificações docentes (só criam variáveis para professores qualificados)
- S03, S04, S06, S07 implementadas no CP-SAT
- S08, S09, S10 alinhadas com Python

### Restrições atualizadas (constraints.py)
- `ContextoRestricoes`: campo `subgrupos` adicionado
- `subgrupo_por_id()`: método auxiliar
- H03: verificada por (turma, subgrupo_id, slot) em vez de apenas (turma, slot)

## Decisões tomadas
- Quando `subgrupo_id` é None, a aula é para toda a turma
- Quando `subgrupo_id` está presente, a aula é apenas para esse subgrupo
- H03 permite que a mesma turma tenha aulas em subgrupos diferentes no mesmo slot

## Escore epistémico
Alta confiança — baseado na análise do documento de auditoria e do código existente.

## Próximos passos
- T040: Implementar contrato SolverResult
- T041: Refinar função objetivo e metaheurísticas
- T042: Avaliação incremental com cache isolado
