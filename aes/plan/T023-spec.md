# AES Plan Spec — T023 Modelo de Dados Alargado

## 1. Sumário Executivo
Estender o modelo de domínio para faculdade: salas específicas por curso, setup/limpeza, almoço protegido, furos, não-periodicidade, indisponibilidades com justificação, contestações.

## 2. Novas Entidades SQLAlchemy
- Room.room_type: "normal" | "laboratorio" | "anatomia"
- Room.allowed_courses: JSON[] (lista de códigos de curso)
- Room.reserved_times: JSON[] (slots já ocupados por outras atividades)
- Room.setup_before: int (minutos)
- Room.cleanup_after: int (minutos)
- Subject.periodicity: "semanal" | "quinzenal" | "modulo_semestre"
- Subject.weeks_active: JSON[] (semanas em que a disciplina ocorre)
- Teacher.availability: JSON (slots disponíveis)
- Teacher.lunch_sacred: bool
- Teacher.commute_time: int (minutos)
- Class.course: str
- Class.weeks_active: JSON[]
- AcademicPeriod: id, type ("semestre"/"trimestre"), start_date, end_date, active_weeks
- Unavailability: id, teacher_id, slot (JSON), justification (enum: deslocamento, folga, almoço, compromisso, doença, outro)
- Dispute: id, teacher_id, assignment_id, reason, justification, status, created_at, resolved_at

## 3. Novas Restrições
- H09: Sala não pode ser usada por curso não permitido
- H10: Setup/limpeza não sobrepõe com aula
- H11: Bloco de almoço protegido para docentes com lunch_sacred
- S-furos: Penalizar gaps entre aulas consecutivas da mesma turma
- S-setup: Penalizar salas sem tempo de setup/limpeza adequado
- S-periodicidade: Disciplinas não-periodicais devem respeitar semanas_ativas

## 4. Testes
- `backend/tests/test_rooms_extended.py` — validação de salas com cursos permitidos
- `backend/tests/test_scheduling_constraints.py` — validação H09-H11, S-furos, S-setup
- `backend/tests/test_periodicity.py` — disciplinas semanais/quinzenais/módulo

## 5. Documentação
- `docs/constraints.md` atualizada com as novas restrições de faculdade
