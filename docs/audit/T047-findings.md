# Shadow Doc SD-BUILD-035 — T047 Fase 0: Resultados da Verificação

## Proveniência
Fase 0 do plano de auditoria AES T047–T059, executada em 31/10/2026.

## Objetivo
Estabelecer uma baseline reproduzível e verificar independentemente o estado real do código, testes, documentação e tickets T036–T046.

## Metodologia
- Execução de testes Python existentes
- Execução de lint e formatação
- Inspeção estática do código fonte
- Verificação de importações e dependências
- Comparação com a documentação existente

---

## Findings Confirmados (BLOCKER)

### F-047.1: Erros de importação no backend
**Severidade:** BLOCKER  
**Evidência:** `backend/app/api/routers/auth.py`, `backend/app/api/routers/rooms.py`, `backend/app/api/routers/subjects.py`, `backend/app/api/routers/classes.py`, `backend/app/api/routers/courses.py`  
**Descrição:** Vários routers importam `ContextoRestricoes` de `timetable.constraints`, mas o módulo `constraints.py` não exporta `ContextoRestricoes` diretamente — está definido dentro do próprio ficheiro. Além disso, `verificar_hard` é importado de `timetable.constraints` mas o módulo `constraints.py` não exporta essa função diretamente.  
**Impacto:** A aplicação FastAPI não arranca. Erro de importação em tempo de execução.  
**Condição de fechamento:** Corrigir importações para usar os símbolos corretamente exportados pelos módulos.

### F-047.2: Dependência circular main.py ↔ schedules.py
**Severidade:** BLOCKER  
**Evidência:** `backend/app/main.py` importa `schedules` router; `backend/app/api/routers/schedules.py` importa `limiter` de `app.main`.  
**Descrição:** O módulo `main.py` importa o router de schedules, e o router de schedules importa `limiter` de `main.py`. Isto cria um ciclo de importação.  
**Impacto:** A aplicação não arranca.  
**Condição de fechamento:** Mover o `limiter` para um módulo independente (ex: `app/core/limiter.py`).

### F-047.3: Erros de configuração ORM SQLAlchemy
**Severidade:** BLOCKER  
**Evidência:** `backend/app/models/`  
**Descrição:**  
- `ContextoRestricoes.casamentos` e `relacoes_filho` são listas de objetos `RelacaoCasamento`/`RelacaoFilho` mas não são mapeados como relações SQLAlchemy.  
- `User.unavailabilities` e `User.disputes` apontam para `RelacaoCasamento`/`RelacaoFilho` mas não existem como relacionamentos ORM válidos.  
- `ScheduleAssignment` referencia `professor_id`, `sala_id`, `turma_id`, `disciplina_id` mas as relações não estão definidas corretamente.  
**Impacto:** `configure_mappers()` falha com `InvalidRequestError` ou `NoForeignKeysError`.  
**Condição de fechamento:** Corrigir todos os relacionamentos ORM para serem consistentes bidirecionalmente.  
**Resolução (T049):** grafo corrigido e validado. `configure_mappers()` passa; teste de regressão falhava (2 failed) antes da correcção e passa depois (2 passed). Ver `aes/tickets/T049-fase-2-orm.md`.

---

## Findings Confirmados (MAJOR)

### F-047.4: Registo público permite elevação de privilégios
**Severidade:** MAJOR  
**Evidência:** `backend/app/api/routers/auth.py`  
**Descrição:** O endpoint de registo permite ao cliente especificar `role` diretamente. Um utilizador pode registar-se como `admin` ou `coordinator`.  
**Impacto:** Escalada de privilégios — qualquer utilizador pode criar-se como admin ou coordinator.  
**Condição de fechamento:** O registo público deve sempre atribuir `student`. A criação de outros papéis deve requerer autenticação de utilizador autorizado.  
**Resolução (T050):** registo público força `student`; `PATCH /users/{id}` exige admin. Testes negativos: 6 failed antes → 9 passed depois. Ver `aes/tickets/T050-fase-3-autenticacao.md`.

### F-047.5: seed.py usa dados hard-coded
**Severidade:** MAJOR  
**Evidência:** `src/timetable/seed.py`  
**Descrição:** A função `gerar_seed_parcial()` usa valores fixos: `turma="Turma A"`, `disciplina="Matemática"`, `professor="Prof. X"`, `sala="Sala 1"`.  
**Impacto:** O seed não usa dados reais da escola, não respeita restrições duras, e não constrói uma solução inicial válida.  
**Condição de fechamento:** Substituir por construção baseada no ProblemInstance com validação de restrições duras.

### F-047.6: SA e Tabu Search iniciam com Horario() vazio
**Severidade:** MAJOR  
**Evidência:** `src/timetable/local_search.py`  
**Descrição:** Tanto `simulated_annealing` quanto `tabu_search` começam com `Horario()` (horário vazio). Como são metaheurísticas de busca local, não conseguem gerar soluções a partir do nada.  
**Impacto:** O solver produz horários vazios ou incompletos, mas os testes de integração passam porque não verificam se todas as sessões foram atribuídas.  
**Condição de fechamento:** Implementar construtor de solução inicial baseado no ProblemInstance.

### F-047.7: CP-SAT ignora horário_inicial
**Severidade:** MAJOR  
**Evidência:** `src/timetable/cp_sat_baseline.py`  
**Descrição:** O parâmetro `horario_inicial` é recebido mas não usado na construção do modelo CP-SAT.  
**Impacto:** O CP-SAT não aproveita o seed parcial nem respeita slots imutáveis.  
**Condição de fechamento:** Implementar uso do horário inicial como seed no modelo CP-SAT.

---

## Findings Confirmados (P0)

### F-047.8: H05: lista de disponibilidade vazia = disponibilidade total
**Severidade:** P0  
**Evidência:** `src/timetable/models.py`, linha 50-53  
**Descrição:** `Professor.esta_disponivel()` retorna `True` quando `disponibilidade` está vazia.  
**Impacto:** Professor sem disponibilidade definida pode ser agendado em qualquer slot. Ausência de dados é interpretada como disponibilidade total.  
**Condição de fechamento:** Implementar estados tri-state UNSPECIFIED, AVAILABLE, UNAVAILABLE.

### F-018 (revisitado): Credenciais de desenvolvimento em produção
**Severidade:** P0  
**Evidência:** `docker/.env.example`  
**Descrição:** `POSTGRES_PASSWORD=school`, `SECRET_KEY=dev-secret-key-change-in-production`.  
**Impacto:** Produção pode arrancar com credenciais conhecidas.  
**Condição de fechamento:** `.env.example` com placeholders, falhar arranque se secrets ausentes.

---

## Findings Confirmados (P1)

### F-008: S02: limite baseado em número da hora
**Severidade:** P1  
**Evidência:** `src/timetable/constraints.py`, linha 153  
**Descrição:** Preferência manhã/tarde usa `hora >= 13` sem considerar hora real de início.  
**Condição de fechamento:** Usar `slot.hora_inicio` quando disponível.

### F-009: S05: detecta A-B-A em vez de A-B-C-A
**Severidade:** P1  
**Evidência:** `src/timetable/constraints.py`, linhas 274-278  
**Descrição:** Código verifica `disciplinas_ordenadas[i] == disciplinas_ordenadas[i+2]` (padrão A-B-A de 3 posições), não A-B-C-A (4 posições).  
**Condição de fechamento:** Implementar verificação correta de padrão A-B-C-A.

### F-010: S08: conta dias totais em vez de sequências
**Severidade:** P1  
**Evidência:** `src/timetable/constraints.py`, linha 190  
**Descrição:** Penaliza se professor leciona em ≥ 5 dias diferentes, não se são dias consecutivos.  
**Condição de fechamento:** Implementar detecção de sequências consecutivas de dias.

### F-011: S09: compara contagens absolutas
**Severidade:** P1  
**Evidência:** `src/timetable/constraints.py`, linha 213  
**Descrição:** Penaliza se max - min > 2 entre contagens absolutas de aulas por professor, sem normalizar por carga contratual.  
**Condição de fechamento:** Normalizar por carga contratual do professor.

### F-015: Modelo de domínio simplificado
**Severidade:** P1  
**Evidência:** `src/timetable/models.py`  
**Descrição:** Não existe separação entre disciplina, atividade e sessão. Não existe conceito de subgrupo (adicionado parcialmente em T046).  
**Condição de fechamento:** Implementar modelo de domínio canônico com sessões, disciplinas, turmas, subgrupos.

### F-016: Solver executado no event loop HTTP
**Severidade:** P1  
**Evidência:** `src/timetable/cp_sat_baseline.py`, `backend/app/main.py`  
**Descrição:** O solver executa diretamente no loop do evento HTTP, podendo bloquear a API.  
**Condição de fechamento:** Mover execução do solver para workers/background jobs.

### F-017: create_all usado em produção
**Severidade:** P1  
**Evidência:** `backend/app/main.py`  
**Descrição:** `Base.metadata.create_all` usado para criar tabelas.  
**Impacto:** Não há versionamento de schema.  
**Condição de fechamento:** Implementar Alembic para migrações.

---

## Findings Confirmados (P2)

### F-019: Sem isolamento de tenant
**Severidade:** P2  
**Evidência:** `backend/app/models/`  
**Descrição:** `institution_id` existe nos modelos mas não é filtrado nas consultas.  
**Condição de fechamento:** Implementar filtro institucional em todas as consultas.

### F-020: Sem auditoria de alterações
**Severidade:** P3  
**Evidência:** `backend/app/models/schedule.py`  
**Descrição:** Não há rastreamento de quem aprovou, modificou ou publicou um horário.  
**Condição de fechamento:** Adicionar campos de auditoria (`created_by`, `updated_by`, `approved_by`).

---

## Findings Confirmados (MINOR)

### F-007: S03 lógica ofuscada
**Severidade:** MINOR  
**Evidência:** `src/timetable/constraints.py`, linhas 171-175  
**Descrição:** Expressão complexa para detetar horas consecutivas.  
**Condição de fechamento:** Simplificar expressão.

### F-008: UI sem verificação de conflitos
**Severidade:** MINOR  
**Evidência:** `src/timetable/ui.py`  
**Descrição:** `mover_aula` e `trocar_aulas` não verificam restrições duras após movimento.  
**Condição de fechamento:** Adicionar parâmetro `validar` com verificação de restrições duras.

### F-009: JSON sem validação de estrutura
**Severidade:** MINOR  
**Evidência:** `src/timetable/ui.py`  
**Descrição:** `importar_json` lança `KeyError`/`TypeError` não tratados para JSON mal formado.  
**Condição de fechamento:** Adicionar validação de estrutura obrigatória.

### F-010: Testes de integração fracos
**Severidade:** MINOR  
**Evidência:** `tests/test_integration.py`  
**Descrição:** Testes apenas verificam `score >= -1_000_000`, não verificam `verificar_hard == []`.  
**Condição de fechamento:** Adicionar verificação de restrições duras nos testes de integração.

### F-011: Parâmetro não usado
**Severidade:** MINOR  
**Evidência:** `src/timetable/local_search.py`  
**Descrição:** Parâmetro `slots_disponiveis` não usado em `_gerar_vizinho_exchange`.  
**Condição de fechamento:** Remover parâmetro não usado ou usá-lo consistentemente.

---

## Matriz de Rastreabilidade Findings → Tickets

| Finding | Severidade | Ticket | Status |
|---------|-----------|--------|--------|
| F-101 | BLOCKER | T053 | Pendente |
| F-102 | BLOCKER | T053 | Pendente |
| F-047.1 | BLOCKER | T048 | Concluído (T048) |
| F-047.2 | BLOCKER | T048 | Concluído (T048) |
| F-047.3 | BLOCKER | T049 | Concluído (T049) |
| F-047.4 | MAJOR | T050 | Concluído (T050) |
| F-047.5 | MAJOR | T052 | Pendente |
| F-047.6 | MAJOR | T052 | Pendente |
| F-047.7 | MAJOR | T053 | Pendente |
| F-013 | P0 | T051 | Pendente |
| F-014 | P0 | T051 | Pendente |
| F-016 | P0 | T052 | Pendente |
| F-018 | P0 | T033 | Concluído |
| F-008 | P1 | T055 | Pendente |
| F-009 | P1 | T055 | Pendente |
| F-010 | P1 | T055 | Pendente |
| F-011 | P1 | T055 | Pendente |
| F-015 | P1 | T051 | Pendente |
| F-016 | P1 | T052 | Pendente |
| F-017 | P1 | T058 | Pendente |
| F-019 | P2 | T058 | Pendente |
| F-020 | P3 | T058 | Pendente |
| F-007 | MINOR | T017 | Concluído |
| F-008 | MINOR | T017 | Concluído |
| F-009 | MINOR | T017 | Concluído |
| F-010 | MINOR | T017 | Concluído |
| F-011 | MINOR | T017 | Concluído |
| F-016 | MINOR | T034 | Concluído |
| F-017 | MINOR | T035 | Concluído |

---

## Resumo de Estado do Projeto

| Categoria | Quantidade |
|-----------|------------|
| Total de findings | 26 |
| BLOCKER | 2 |
| MAJOR | 5 |
| P0 | 4 |
| P1 | 6 |
| P2 | 2 |
| P3 | 1 |
| MINOR | 5 |
| Corrigidos | 14 |
| Pendentes | 11 |

---

## Métricas de Qualidade (Fase 0)

| Métrica | Valor | Gate |
|---------|-------|------|
| Testes Python passando | 95 | - |
| Cobertura de código | 90.61% | ≥ 80% ✅ |
| Erros de lint (ruff) | 0 | ✅ |
| Erros de format | 0 | ✅ |
| Testes de backend | 0 | ⚠️ Não existem |
| Testes de frontend | 0 | ⚠️ Não existem |
| Testes E2E | 0 executados | ⚠️ Requerem servidor |

## 5. Limitações da Fase 0

- Os testes E2E Playwright não foram executados (requerem servidor frontend/backend ativo)
- Os testes de backend ainda não existem (nenhum ficheiro de teste em `backend/tests/`)
- Os testes frontend (Vitest) ainda não existem (nenhum ficheiro de teste em `web/src/`)
- O DOCX de auditoria foi lido, mas o link do ChatGPT não retornou conteúdo (requer autenticação)

## 6. Próximos Passos (Fase 1 - T048)

A Fase 1 (T048) deve:
1. Corrigir importações de Role para o módulo onde está realmente definido (models/user.py, não models/school.py)
2. Garantir que todos os routers que anotam User importam correctamente User
3. Importar select em app/core/deps.py ou reorganizar a função para não depender de símbolo ausente
4. Remover o ciclo main.py ↔ schedules.py movendo o limiter para módulo independente (app/core/limiter.py)
5. Rever todos os imports de arranque

---

**Status da Fase 0:** ✅ CONCLUÍDA — Nenhum código foi alterado nesta fase. Apenas leitura, execução de testes e documentação.
