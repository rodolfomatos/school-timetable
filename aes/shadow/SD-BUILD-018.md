# Shadow Doc SD-BUILD-018 — Fase 4: Resultado e Ciclo de Vida do Solver (T040)

## Proveniência
Fase 4 do plano de auditoria (DOCX seção 11), concluída em 31/10/2026.

## O que foi construído

### objective.py atualizado
- `Avaliacao` dataclass com: `viavel`, `violacoes_hard`, `penalidades_moles`, `score`
- `MUITO_NEGATIVO = -1_000_000` para score de soluções inviáveis
- `avaliar_com_cache()`: evita recálculo de horários já vistos
- `limpar_cache_avaliacao()`: limpa cache entre execuções independentes
- `_chave_horario()`: gera chave hashável ordenada por todas as aulas
- `avaliar()`: retorna `Avaliacao` com score separado de violações duras

### Decisões tomadas
- Score negativo para soluções inviáveis (MUITO_NEGATIVO - soma_penalidades)
- Score negativo para soluções viáveis (-soma_penalidades)
- Score 0 para solução perfeita (sem violações duras nem moles)
- Cache por chave hashável do horário (tupla ordenada de aulas)
- Cache limpo entre execuções independentes

## Escore epistémico
Alta confiança — baseado na especificação do documento de auditoria e na implementação existente.

## Próximos passos
- T041: Refinar função objetivo e metaheurísticas (priorização lexicográfica)
- T042: Avaliação incremental com cache isolado por instância de problema
- T043: Backend e operação (solver assíncrono, migrações Alembic, segurança)
