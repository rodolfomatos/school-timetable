# Decisões de Arquitetura — school-timetable

**Data:** 31 de outubro de 2026  
**Fase:** Fase 9 — Entregáveis (T045)

---

## 1. Visão Geral

O school-timetable é um sistema de geração e gestão de horários escolares/acadêmicos composto por:
- Solver Python (Tabu Search, Simulated Annealing, CP-SAT/OR-Tools)
- API FastAPI com autenticação JWT e RBAC
- Frontend React com design system @ilabuporto/design-system
- PostgreSQL + Docker Compose
- Testes E2E com Playwright

---

## 2. Decisões de Arquitetura

### 2.1 Linguagem e Stack
- **Python 3.10+** para o solver e backend
- **TypeScript/React** para o frontend
- **PostgreSQL** para banco de dados
- **Docker Compose** para implantação

**Justificativa:** Python é a linguagem nativa do ecossistema de otimização (OR-Tools, scipy, numpy). FastAPI oferece desempenho e documentação automática. React com TypeScript oferece tipagem estática e ecossistema maduro.

### 2.2 Solver: CP-SAT + Metaheurísticas
- **CP-SAT (OR-Tools):** Solver exato para instâncias pequenas, linha de base verificável
- **Tabu Search:** Busca local com memória de curto prazo (lista tabu)
- **Simulated Annealing:** Busca local com aceitação probabilística de soluções piores

**Justificativa:** Diferentes algoritmos têm diferentes pontos fortes. CP-SAT garante viabilidade e optimalidade para instâncias pequenas. Metaheurísticas são mais rápidas para instâncias grandes.

### 2.3 Função Objetivo Aditiva
- Score = -Σ(penalidade × peso)
- Restrições duras: score = -infinito (representado por inteiro muito negativo)
- Restrições moles: penalidade aditiva

**Justificativa:** Evita o problema de números astronômicos (produto multiplicativo de pesos) relatado na literatura acadêmica. Permite ajuste fino de pesos por categoria de restrição.

### 2.4 Autenticação JWT com Cookies httpOnly
- Token de acesso em cookie httpOnly (não acessível via JavaScript)
- Token de refresh para renovação
- Logout limpa cookies

**Justificativa:** Previne roubo de token via XSS. Cookies httpOnly são inacessíveis a scripts maliciosos.

### 2.4 RBAC (Role-Based Access Control)
- Papéis: admin, coordinator, teacher, student
- Verificação de papel em cada rota sensível
- Autorização por recurso (ex: professor só contesta aulas atribuídas a ele)

**Justificativa:** Isolamento de funcionalidades por papel de usuário. Previne acesso não autorizado a operações administrativas.

### 2.5 Docker Compose para Implantação
- Serviços: postgres, backend, frontend
- Volumes para persistência de dados
- Health checks para ordenação de inicialização

**Justificativa:** Implantação simples em ambiente local (on-premise) ou SaaS. Isolamento de dependências.

### 2.6 Design System @ilabuporto/design-system
- Componentes React pré-construídos (Button, Table, Modal, Card, etc.)
- Tokens de cor institucional U.Porto (brand #009FDF)
- Tailwind CSS para estilização adicional

**Justificativa:** Consistência visual com identidade institucional. Reduz tempo de desenvolvimento de interface.

---

## 3. Decisões Pendentes

### 3.1 Multi-tenancy
**Decisão:** Não implementado ainda. Modelo `Organization` precisa ser adicionado como fronteira de isolamento.
**Impacto:** Dificulta uso em modo SaaS por múltiplas instituições.

### 3.2 Migrações Alembic
**Decisão:** Configuradas mas não utilizadas em produção (create_all usado no startup).
**Impacto:** Evolução de schema em produção é arriscada sem migrações versionadas.

### 3.3 Avaliação Incremental
**Decisão:** Cache de avaliação implementado, mas não avaliação incremental verdadeira (delta de score).
**Impacto:** Performance limitada para instâncias grandes (centenas de aulas).

### 3.4 Priorização Lexicográfica
**Decisão:** Função objetivo aditiva simples. Priorização lexicográfica (Nível 0: hard, Nível 1-4: soft) não implementada.
**Impacto:** Violações de restrições moles podem ser compensadas entre si de forma inadequada.

---

## 4. Regras de Engenharia

1. Nenhum código sem ticket AES associado
2. Nenhuma alteração de código sem teste correspondente
3. Nenhuma restrição dura violada em solução publicada
4. Validador independente separado do solver
5. Dados de teste sintéticos (não dados reais de alunos/docentes)
6. Commits lógicos por fase
7. Documentação atualizada com cada alteração de domínio
