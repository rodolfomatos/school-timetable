# AES Plan Spec — T005 Metaheurística Principal

## 1. Sumário Executivo
Refinar as metaheurísticas de busca local (Tabu Search e Simulated Annealing) em `local_search.py` com operadores de exchange/modify, respeito a slots imutáveis, critério de parada satisficing e lista tabu FIFO adequada.

## 2. Operadores de Movimento

### Exchange (movimento principal)
Trocar os slots de duas aulas aleatórias. Mais comum que modify segundo a literatura.

### Modify (movimento secundário)
Mover uma aula para outro slot aleatório.

## 3. Slots Imutáveis (Seed)
Aulas em slots imutáveis (do seed T006) não podem ser alteradas pelos operadores de busca.

## 4. Critério de Parada (Satisficing)
- Limite de tempo configurável (default 60s)
- Limite de iterações sem melhoria no score global (default 500)
- Score alvo opcional: parar se score >= limiar_satisficing

## 5. Lista Tabu
- FIFO com tamanho configurável (default 50)
- Critério de aspiração: aceita movimento tabu se melhora o score global
- Chave de tabu: (turma, disciplina, slot_origem, slot_destino) para exchange

## 6. Simulated Annealing
- Temperatura inicial configurável (default 1000.0)
- Resfriamento geométrico (default 0.995)
- Critério de aceitação: aceita se melhor, ou com probabilidade exp(delta/temperatura) se pior

## 7. Interface
Ambas as funções mantêm a assinatura existente:
`resolver(horario_inicial, ctx, slots, tempo_limite_segundos) -> Horario`

## 8. Testes
- Teste de exchange não altera slots imutáveis
- Teste de não-violação de restrições duras
- Teste de parada por não-melhoria
- Teste de qualidade: score não piora após execução
