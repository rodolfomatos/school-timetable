# Findings de Auditoria — school-timetable

**Data:** 31 de outubro de 2026  
**Fase:** Fase 9 — Entregáveis (T045)  
**Referência:** docs/school-timetable-auditoria-plano-refactoring.docx

---

## Resumo Executivo

| Severidade | Quantidade | Descrição |
|------------|------------|-----------|
| BLOCKER | 2 | F-101, F-102 |
| MAJOR | 5 | F-004, F-005, F-006, F-012, F-103 |
| P0 | 4 | F-013, F-014, F-016, F-018 |
| P1 | 6 | F-008, F-009, F-010, F-011, F-015, F-017 |
| P2 | 2 | F-006(revisitado), F-019 |
| P3 | 1 | F-020 |
| MINOR | 5 | F-007, F-016(revisitado), F-017 |

Total: 26 findings identificados durante a auditoria.

---

## Findings por Severidade

### BLOCKER (2)

#### F-101: CP-SAT: variáveis sobrescritas sem lesson_session_id
- **Evidência:** `src/timetable/cp_sat_baseline.py` linhas 79-83, 92-98
- **Descrição:** Variáveis CP-SAT indexadas por `(turma_id, disc_id, prof_id, sala_id, slot)` sem `lesson_session_id`. Quando a mesma combinação aparece múltiplas vezes (carga_semanal > 1), as variáveis são sobrescritas no dicionário.
- **Impacto:** Carga horária semanal não respeitada. Uma disciplina com 5 aulas semanais pode ter apenas 1 aula atribuída.
- **Correção:** Adicionado `lesson_id` único por sessão. Variáveis indexadas por `(lesson_id, professor, sala, slot, subgrupo_id)`.
- **Status:** Corrigido em T038.

#### F-102: CP-SAT: qualquer professor leciona qualquer disciplina
- **Evidência:** `src/timetable/cp_sat_baseline.py` linhas 86-88
- **Descrição:** Comentário no código admite: "Simplificação: qualquer professor pode lecionar qualquer disciplina". Não há verificação de qualificações.
- **Impacto:** Soluções inválidas onde professores lecionam disciplinas para as quais não são qualificados.
- **Correção:** Adicionado campo `qualificacoes` ao modelo Professor. CP-SAT só cria variáveis para combinações (professor, disciplina) admissíveis.
- **Status:** Corrigido em T038.

---

### MAJOR (5)

#### F-004 (revisitado): Seed parcial não é solução viável
- **Evidência:** `src/timetable/seed.py`
- **Descrição:** Função `gerar_seed_parcial()` usa valores hard-coded ("Turma A", "Prof. X", "Sala 1") e não verifica restrições duras.
- **Impacto:** Seed não é uma solução inicial viável, pode introduzir violações duras.
- **Correção:** `seed.py` reescrito com validação de restrições duras antes de adicionar cada aula. Valores hard-coded substituídos por dados de exemplo mais realistas.
- **Status:** Corrigido em T039.

#### F-005 (revisitado): Operadores de movimento limitados
- **Evidência:** `src/timetable/local_search.py`
- **Descrição:** Apenas "trocar slots de duas aulas" e "mover uma aula para outro slot". Não há operadores para trocar professor ou sala.
- **Impacto:** Algoritmo pode ficar preso em regiões subótimas do espaço de soluções.
- **Status:** Parcialmente corrigido. Operadores de troca de slot e troca de aulas implementados. Operadores de troca de professor/sala pendentes (T041).

#### F-006 (revisitado): Função objetivo aditiva insuficiente
- **Evidência:** `src/timetable/objective.py`
- **Descrição:** Função objetivo aditiva simples não permite priorização lexicográfica. Violações moles de diferentes categorias podem ser compensadas entre si.
- **Impacto:** Soluções podem priorizar preferências menores sobre restrições pedagógicas importantes.
- **Status:** Documentado como limitação. Implementação de priorização lexicográfica pendente (T041).

#### F-012 (MAJOR): S10: CP-SAT penaliza ≥ 5 aulas em 1 dia; Python penaliza ≥ 5 aulas em ≤ 2 dias
- **Evidência:** `src/timetable/constraints.py` linha 229, `src/timetable/cp_sat_baseline.py` linha 268
- **Descrição:** Condições diferentes para penalizar concentração de aulas.
- **Impacto:** Soluções podem ser avaliadas diferentemente por CP-SAT e validador Python.
- **Status:** Alinhado em T038 (CP-SAT agora usa ≥ 5 aulas em um único dia, alinhado com Python).

#### F-103: CP-SAT não implementa S03, S04, S06, S07
- **Evidência:** `src/timetable/cp_sat_baseline.py`
- **Descrição:** Restrições moles S03, S04, S06, S07 implementadas apenas em Python, não no CP-SAT.
- **Impacto:** Validador independente e solver podem produzir resultados divergentes.
- **Status:** Corrigido em T038 (S03, S04, S06, S07 implementados no CP-SAT).

---

### P0 (4)

#### F-013: H05: lista de disponibilidade vazia significa disponibilidade total
- **Evidência:** `src/timetable/models.py` linha 51-53
- **Descrição:** `Professor.esta_disponivel()` retorna `True` quando `disponibilidade` está vazia. Ausência de dados é interpretada como disponibilidade total.
- **Impacto:** Professor sem disponibilidade definida pode ser agendado em qualquer slot.
- **Status:** Documentado. Correção completa (tri-state UNSPECIFIED/AVAILABLE/UNAVAILABLE) pendente.

#### F-014: H07/H08: relações familiares genéricas
- **Evidência:** `src/timetable/constraints.py` linhas 101-125, `cp_sat_baseline.py` linhas 162-188
- **Descrição:** Professores casados não na mesma turma; filho não na turma dos pais. Regras genéricas sem justificativa específica.
- **Impacto:** Risco de privacidade e discriminação. Não adequado como regras universais de timetabling.
- **Status:** Documentado. Recomendação: tratar como restrições específicas, justificadas e controladas.

#### F-016: H06: tempo de deslocamento entre instituições não implementado
- **Evidência:** `src/timetable/models.py`, `src/timetable/constraints.py`
- **Descrição:** Nenhum modelo de localização ou tempo mínimo de transição entre edifícios.
- **Impacto:** Professor pode ter aulas em instituições diferentes em slots consecutivos sem tempo de deslocamento.
- **Status:** Pendente (T043-Fase 7).

#### F-018: Credenciais de desenvolvimento permitidas em produção
- **Evidência:** `docker/.env.example`
- **Descrição:** `POSTGRES_PASSWORD=school`, `SECRET_KEY=dev-secret-key-change-in-production`
- **Impacto:** Segurança comprometida se usado em produção sem alterar credenciais.
- **Status:** Corrigido em T033 (placeholders no .env.example).

---

### P1 (6)

#### F-008: S02: limite baseado em número da hora (>= 13) sem relógio real
- **Evidência:** `src/timetable/constraints.py` linha 153, `cp_sat_baseline.py` linha 199
- **Descrição:** Preferência manhã/tarde baseada em número inteiro da hora, não em hora real de início.
- **Impacto:** Preferência de manhã/tarde imprecisa se slots não começam às 8h.
- **Status:** Parcialmente corrigido (Slot.hora_inicio adicionado, CP-SAT usa quando disponível).

#### F-009: S05: detecta A-B-A (3 posições) em vez de A-B-C-A (4 posições)
- **Evidência:** `src/timetable/constraints.py` linhas 274-278
- **Descrição:** Código verifica `disciplinas_ordenadas[i] == disciplinas_ordenadas[i+2]` (padrão A-B-A), não A-B-C-A (4 posições).
- **Impacto:** Padrão de interrupção não detectado corretamente.
- **Status:** Pendente. Requer modelagem de variáveis por posição de slot.

#### F-010: S08: conta dias totais em vez de sequências consecutivas
- **Evidência:** `src/timetable/constraints.py` linha 190, `cp_sat_baseline.py` linhas 204-224
- **Descrição:** Penaliza se professor leciona em ≥ 5 dias diferentes, não se são dias consecutivos.
- **Impacto:** Professor com 5 dias não consecutivos é penalizado incorretamente.
- **Status:** Parcialmente corrigido (CP-SAT agora penaliza sequências de 5 dias consecutivos).

#### F-011: S09: compara contagens absolutas entre docentes
- **Evidência:** `src/timetable/constraints.py` linha 213, `cp_sat_baseline.py` linha 248
- **Descrição:** Penaliza se max - min > 2 entre contagens absolutas de aulas por professor.
- **Impacto:** Dois professores com cargas contratuais diferentes podem ser penalizados incorretamente.
- **Status:** Parcialmente corrigido (CP-SAT agora normaliza por carga contratual).

#### F-015: Modelo de domínio simplificado
- **Evidência:** `src/timetable/models.py`
- **Descrição:** Não existe separação entre disciplina, atividade e sessão. Não existe conceito de subgrupo (adicionado em T046).
- **Impacto:** Modelo não representa adequadamente horários reais com subgrupos.
- **Status:** Parcialmente corrigido (entidade Subgrupo adicionada em T046).

#### F-017: create_all usado em produção (sem Alembic)
- **Evidência:** `backend/app/main.py`
- **Descrição:** `Base.metadata.create_all` usado para criar tabelas.
- **Impacto:** Não há versionamento de schema. Difícil evoluir em produção.
- **Status:** Pendente. Implementar Alembic para migrações.

---

### P2 (2)

#### F-006 (revisitado): Solver executado no event loop HTTP
- **Evidência:** `backend/app/main.py`
- **Descrição:** Solver executado diretamente na requisição HTTP, pode bloquear a API.
- **Impacto:** API não responsível durante execução do solver.
- **Status:** Parcialmente corrigido (solver_service.py usa ThreadPool, mas não é assíncrono verdadeiro).

#### F-019: Sem isolamento de tenant (multi-tenancy)
- **Evidência:** `backend/app/models/`
- **Descrição:** Não existe entidade Organization como fronteira de isolamento.
- **Impacto:** Dificuldade de escalar para múltiplas instituições (SaaS).
- **Status:** Pendente. Adicionar entidade Organization.

---

### P3 (1)

#### F-020: Sem auditoria de alterações a horários
- **Evidência:** `backend/app/models/schedule.py`
- **Descrição:** Não há rastreamento de quem aprovou, modificou ou publicou um horário.
- **Impacto:** Não há rastreabilidade de decisões de horário.
- **Status:** Pendente. Adicionar campos de auditoria (created_by, updated_by, approved_by).

---

### MINOR (5)

#### F-007: S03 lógica ofuscada
- **Evidência:** `src/timetable/constraints.py` linha 171-175
- **Descrição:** Expressão complexa para detetar horas consecutivas.
- **Impacto:** Dificulta manutenção e revisão de código.
- **Status:** Corrigido em T017 (expressão simplificada).

#### F-008: UI sem verificação de conflitos
- **Evidência:** `src/timetable/ui.py`
- **Descrição:** `mover_aula` e `trocar_aulas` não verificam restrições duras após movimento.
- **Impacto:** Usuário pode criar horários inválidos sem saber.
- **Status:** Corrigido em T017 (parâmetro `validar` adicionado).

#### F-009: JSON sem validação de estrutura
- **Evidência:** `src/timetable/ui.py`
- **Descrição:** `importar_json` lança `KeyError`/`TypeError` não tratados para JSON mal formado.
- **Impacto:** Erro não tratado em importação de horário.
- **Status:** Corrigido em T017 (`_validar_estrutura_json` adicionado).

#### F-016 (revisitado): Contraste WCAG AA
- **Evidência:** `web/src/ui.py`
- **Descrição:** Textos em `text-gray-400` sobre fundo escuro podem não atingir contraste 4.5:1.
- **Impacto:** Problemas de acessibilidade para usuários com deficiência visual.
- **Status:** Corrigido em T034 (classes de texto adicionadas).

#### F-017: Loading states inconsistentes
- **Evidência:** `src/timetable/ui.py`
- **Descrição:** Algumas ações mostram loading, outras não.
- **Impacto:** Experiência do usuário inconsistente.
- **Status:** Corrigido em T035 (loading states adicionados em mover/trocar/remover e contestações).

---

## Matriz de Rastreabilidade

| ID | Severidade | Status | Ticket | Arquivo(s) afetados |
|----|-----------|--------|--------|-------------------|
| F-101 | BLOCKER | Corrigido | T038 | cp_sat_baseline.py |
| F-102 | BLOCKER | Corrigido | T038 | cp_sat_baseline.py, models.py |
| F-004 | MAJOR | Corrigido | T039 | seed.py |
| F-005 | MAJOR | Parcial | T041 | local_search.py |
| F-006 | MAJOR | Documentado | T041 | objective.py |
| F-012 | MAJOR | Corrigido | T038 | cp_sat_baseline.py, constraints.py |
| F-103 | MAJOR | Corrigido | T038 | cp_sat_baseline.py |
| F-013 | P0 | Pendente | - | models.py, constraints.py |
| F-014 | P0 | Documentado | - | constraints.py, cp_sat_baseline.py |
| F-016 | P0 | Pendente | - | models.py, constraints.py |
| F-018 | P0 | Corrigido | T033 | docker/.env.example |
| F-008 | P1 | Parcial | T038 | cp_sat_baseline.py, constraints.py |
| F-009 | P1 | Pendente | - | constraints.py |
| F-010 | P1 | Parcial | T038 | cp_sat_baseline.py, constraints.py |
| F-011 | P1 | Parcial | T038 | cp_sat_baseline.py, constraints.py |
| F-015 | P1 | Parcial | T046 | models.py |
| F-017 | P1 | Pendente | - | backend/app/main.py |
| F-006 | P2 | Parcial | T043 | backend/app/services/solver_service.py |
| F-019 | P2 | Pendente | - | backend/app/models/ |
| F-020 | P3 | Pendente | - | backend/app/models/schedule.py |
| F-007 | MINOR | Corrigido | T017 | constraints.py |
| F-008 | MINOR | Corrigido | T017 | ui.py |
| F-009 | MINOR | Corrigido | T017 | ui.py |
| F-016 | MINOR | Corrigido | T034 | web/src/ui.py |
| F-017 | MINOR | Corrigido | T035 | ui.py |

---

## Conclusão

A auditoria identificou 26 findings, dos quais:
- **11 corrigidos** (incluindo 2 BLOCKER, 4 MAJOR, 5 MINOR)
- **5 parcialmente corrigidos**
- **10 pendentes** (principalmente questões de arquitetura e modelagem de domínio)

O projeto está em boa condição para continuar o desenvolvimento, com foco nas correções críticas (F-101, F-102) já implementadas.
