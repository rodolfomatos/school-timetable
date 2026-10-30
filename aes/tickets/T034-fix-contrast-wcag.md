# Ticket T034 — Fix F-016 (MINOR): Contraste WCAG AA

## Contexto
Finding F-016 (MINOR): Alguns textos em `text-gray-400` sobre fundo escuro podem não atingir o contraste WCAG AA (4.5:1 para texto normal).

## Objetivo
Auditar e corrigir o contraste de cores no frontend:
- Revisar cores de texto em componentes e páginas
- Garantir contraste mínimo 4.5:1 para texto normal e 3:1 para texto grande
- Usar ferramenta de verificação de contraste

## Critérios de Aceitação
1. Nenhum texto com contraste abaixo de 4.5:1 em fundo escuro
2. Cores de texto ajustadas para `text-gray-300` ou superior em fundos escuros
3. Documentar no README que o contraste foi auditado
4. `make lint` passa

## Fase atual
Plan → Build.
