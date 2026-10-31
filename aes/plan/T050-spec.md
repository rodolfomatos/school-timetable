# AES Plan Spec — T050 Fase 3: Autenticação e privilégios

## 1. Sumário Executivo
Impedir auto-elevação de privilégios e garantir que a identidade autenticada é a fonte de autoridade para operações administrativas.

## 2. Objetivo
- Registo público atribui sempre student (ou papel público de menor privilégio definido pelo produto), ignorando/rejeitando qualquer role enviado pelo cliente.
- Criação/alteração de teacher, coordinator e admin apenas por actor autorizado.
- Não confiar em institution_id, user_id, resolved_by ou role fornecidos pelo cliente quando devem derivar da sessão autenticada.
- Remover IDs hard-coded, incluindo resolved_by = 1.
- Rever cookies: Secure por configuração de ambiente, HttpOnly, SameSite, domínio e expiração.
- Rever CSRF quando autenticação baseada em cookies é usada.
- Garantir autorização por objecto e por instituição, não apenas por endpoint.

## 3. Critérios de Aceitação
[ ] Tentativa de registo com role=admin não cria administrador.
[ ] Tentativa de registo com role=coordinator não cria coordenador.
[ ] Só actor autorizado altera papéis.
[ ] Operações de resolução guardam o ID do utilizador autenticado.
[ ] Testes negativos cobrem escalada horizontal e vertical.
[ ] Configuração de cookies é segura em produção e testável em ambiente local.
[ ] Eventos sensíveis ficam auditados.

## 4. Fase atual
Plan → Build → Verify.
