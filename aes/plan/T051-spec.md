# AES Plan Spec — T051 Fase 3: Modelo de domínio e integração

## 1. Sumário Executivo
Criar uma camada de domínio canónica, independente do ORM, que traduza os dados institucionais num problema de timetabling completo e consistente.

## 2. Objetivo
- Criar DTOs/modelos de entrada do solver independentes de SQLAlchemy.
- Construir contexto a partir de relações reais: turma ↔ curso ↔ disciplina; docente ↔ qualificações ↔ sessões; sala ↔ capacidade/equipamento/disponibilidade.
- Deixar de combinar indiscriminadamente todas as turmas com todas as disciplinas.
- Carregar e aplicar indisponibilidades persistidas e additional_unavailabilities.
- Modelar qualificações docentes de forma explícita.
- Modelar carga lectiva em unidades claras (minutos/horas de contacto e número de sessões), sem inferir carga a partir de commute_time.
- Validar dados em falta e inconsistências antes de chamar o solver.
- Definir identificador e versão imutável do problema de optimização.

## 3. Critérios de Aceitação
[ ] O solver recebe um ProblemInstance/DTO sem dependência de sessão ORM.
[ ] Só são criadas sessões para relações curriculares válidas.
[ ] Docentes não qualificados não são elegíveis.
[ ] Indisponibilidades persistidas e adicionais são aplicadas.
[ ] Capacidade e requisitos de sala são transportados para o domínio.
[ ] Dados incompletos produzem diagnóstico explícito.
[ ] Testes provam que não há mistura de cursos/turmas/disciplinas.

## 4. Fase atual
Plan → Build → Verify.
