# AES Plan Spec — T048 Fase 1: Bootstrap e imports do backend

## 1. Sumário Executivo
Garantir que a aplicação FastAPI importa, inicializa e resolve as dependências sem imports inválidos, nomes ausentes ou ciclos de importação.

## 2. Objetivo
- Corrigir importações de Role para o módulo onde está realmente definido (models/user.py, não models/school.py).
- Garantir que todos os routers que anotam User importam correctamente User.
- Importar select em app/core/deps.py ou reorganizar a função para não depender de símbolo ausente.
- Remover o ciclo main.py ↔ api/routers/schedules.py movendo o limiter para módulo independente (app/core/limiter.py ou equivalente).
- Rever todos os imports de arranque, não apenas os primeiros erros detectados.
- Evitar imports laterais de main.py a partir de routers/serviços.

## 3. Critérios de Aceitação
[ ] python -c "from app.main import app" termina com exit code 0.
[ ] A aplicação arranca com configuração de teste.
[ ] Todos os routers são registados.
[ ] Um teste de endpoint protegido resolve dependências sem NameError/ImportError.
[ ] Não existe import circular entre main.py, routers e serviços.
[ ] Testes de importação são executados em CI.

## 4. Fase atual
Plan → Build → Verify.
