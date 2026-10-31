# Shadow Doc SD-BUILD-015 — Fase 3: Seed e Validador Independente (T039)

## Proveniência
Fase 3 do plano de auditoria (DOCX seção 11), iniciada em 31/10/2026.

## Objetivo
Substituir o seed esqueleto por um construtor de soluções iniciais baseado em dados reais, e implementar um validador independente separado do solver CP-SAT.

## Decisões tomadas
- seed.py: Removidos valores hard-coded ("Turma A", "Prof. X", etc.)
- seed.py: Adicionada validação de restrições duras antes de adicionar cada aula
- seed.py: Aceita contexto opcional para verificação de restrições
- Próximo: Criar validador independente separado do solver CP-SAT
- Próximo: Criar fixtures de soluções válidas e inválidas

## Escore epistémico
Alta confiança — baseado na análise do documento de auditoria e do código existente.

## Próximos passos
- Implementar validador independente (não usar a mesma lógica do CP-SAT)
- Criar fixtures de soluções válidas e inválidas
- Validar que o validador independente detecta violações que o CP-SAT poderia perder
