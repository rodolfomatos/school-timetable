# Shadow Doc SD-BUILD-026 — T050 Fase 3: Autenticação e privilégios

## Proveniência
Fase 3 do plano de auditoria AES T047–T059, iniciada em 31/10/2026.

## Objetivo
Impedir auto-elevação de privilégios e garantir que a identidade autenticada é a fonte de autoridade para operações administrativas.

## Decisões tomadas
- Registo público atribui sempre student.
- Criação/alteração de teacher, coordinator e admin apenas por actor autorizado.
- Não confiar em institution_id, user_id, resolved_by ou role fornecidos pelo cliente.
- Remover IDs hard-coded, incluindo resolved_by = 1.
- Rever cookies: Secure por configuração de ambiente, HttpOnly, SameSite, domínio e expiração.
- Rever CSRF quando autenticação baseada em cookies é usada.

## Escore epistémico
Alta confiança — baseada na análise de segurança e autenticação.

## Próximos passos
- T051: Modelo de domínio e integração
