# Ticket T031 — Fix F-013 (MAJOR): Sanitização de entrada XSS

## Contexto
Finding F-013 (MAJOR): Formulários de contestação aceitam texto livre sem sanitização, permitindo XSS refletido quando o admin visualiza a contestação.

## Objetivo
Adicionar sanitização de entrada:
- Frontend: instalar `dompurify` e sanitizar campos de texto livre (motivo de contestação, razão de indisponibilidade) antes de exibir
- Backend: validar e sanitizar campos de texto nas schemas Pydantic (rejeitar tags HTML)
- Testes: verificar que entradas com `<script>` são bloqueadas ou sanitizadas

## Critérios de Aceitação
1. `dompurify` instalado no frontend
2. Campos de texto livre sanitizados antes de renderizar (motivo, razão)
3. Backend valida e rejeita conteúdos com tags HTML nos campos de texto
4. Testes de unidade para sanitização
5. `make lint` e `make test` passam

## Fase atual
Plan → Build.
