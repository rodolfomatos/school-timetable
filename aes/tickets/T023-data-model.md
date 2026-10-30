# Ticket T023 — Modelo de Dados Alargado (Faculdade)

## Contexto
O modelo atual cobre escolas secundárias. Para faculdades, precisamos de salas específicas por disciplina/curso, tempos de setup/limpeza, hora do almoço protegida, minimização de furos, não-periodicidade (semanas/trimestres, módulos), e salas com tempos reservados.

## Objetivo
Estender o modelo de domínio no backend com:
- Sala: capacidade, tipo (normal/laboratório/anatomia), cursos_permitidos, tempos_reservados, tempo_setup_antes, tempo_limpeza_depois
- Disciplina: tipo_sala_requerida, periodicidade (semanal/quinzenal/módulo_semestre), carga_semanal, semanas_ativas
- Docente: disponibilidade por slot, dia_folga_preferido, preferência_manha/tarde, hora_almoço_sagrada, tempo_deslocamento
- Turma: curso, ano, número_alunos, semanas_ativas
- Período letivo: tipo (semestre/trimestre), semanas_ativas, datas_inicio/fim
- Indisponibilidade docente: slot, justificação_predefinida
- Contestação: slot, motivo, estado (pendente/aceita/rejeitada)

## Critérios de Aceitação
1. Esquema SQLAlchemy para todas as entidades acima
2. Migrações Alembic configuradas
3. Endpoints CRUD para todas as novas entidades
4. Validação de restrições: sala não pode ser usada por curso não permitido, setup/limpeza bloqueia slots adjacentes, almoço protege intervalo
5. Testes de unidade para o modelo e validações
6. Documentação no `docs/constraints.md` atualizada com as novas restrições de faculdade

## Riscos (Hostile Analysis)
- Conflito de salas (duas aulas na mesma sala ao mesmo tempo) → mitigação: restrição H02 no solver
- Setup/limpeza sobreposto com aula → mitigação: gerar blocos de bloqueio técnicos automaticamente
- Furos excessivos para estudantes → mitigação: restrição mole S-furos na função objetivo
- Não-periodicidade ignorada → mitigação: gerar semanas separadas no solver

## Fase atual
Plan → Build.
