# Shadow Doc SD-BUILD-037 — T050 Fase 3: Autenticação e privilégios

## Proveniência
Fase 3 do plano de auditoria AES T047–T059, concluída em 31/10/2026 sobre o
commit `4842875` (T049 incluído).

## Objetivo
Eliminar auto-elevação de privilégios e fazer da identidade autenticada a única
fonte de autoridade em operações sensíveis.

## Decisões tomadas
- O registo público nunca aceita `role`: força sempre `student` e regista em log
  qualquer tentativa de papel elevado. Alternativa rejeitada: devolver 403, que
  revelaria a política de papéis sem necessidade e quebraria clientes legítimos
  que enviem o campo por omissão.
- A resolução de contestações passa a usar `current_user.id`; o placeholder
  `resolved_by = 1` foi removido.
- `Secure` dos cookies é derivado de `ENVIRONMENT`, mantendo testes locais
  possíveis sem HTTPS.
- O login passa a emitir refresh cookie; sem isso, `/auth/refresh` só funcionava
  via header e o fluxo documentado por cookie estava quebrado.
- CSRF: `SameSite=Lax` + CORS sem wildcard. Token double-submit fica registado
  como trabalho futuro, para não alterar o contrato do frontend neste ticket.
- Testes usam `example.com` porque o validador de email rejeita o TLD reservado
  `.test`; continuam a ser fixtures sintéticos, sem dados reais.

## Evidência
- `backend/tests/test_auth_security.py`: 6 failed no código anterior, 9 passed
  após a correcção.
- `ruff` → `All checks passed!`.
- `from app.main import app` → `APP_IMPORT_OK 14`.
- Suite canónica → 90.59% de cobertura.

## Escore epistémico
Alta confiança — cada critério de aceitação tem teste executável, incluindo
escalada horizontal (utilizador comum altera papéis) e vertical (docente resolve
a própria contestação).

## Próximos passos
- T051: modelo de domínio e integração (F-013, F-014, F-015).
