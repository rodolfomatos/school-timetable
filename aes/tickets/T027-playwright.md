# Ticket T027 — Testes E2E com Playwright

## Contexto
A interface web deve ser testada em fluxos completos, não apenas em unidades isoladas. O Playwright permite testar o browser real com o design system renderizado.

## Objetivo
Criar `e2e/` com testes Playwright para:
1. Fluxo completo: login docente → marcar indisponibilidade → ver horário → contestar slot → admin aceita → horário atualizado
2. Fluxo admin: login admin → gerir utilizadores → criar sala → gerar horário → publicar
3. Fluxo estudante: login estudante → ver horário da turma → receber notificação de alteração
4. Teste de acessibilidade básica (navegação por teclado, contraste)
5. Teste de responsividade (mobile/desktop)

## Critérios de Aceitação
1. `e2e/playwright.config.ts` configurado
2. Pelo menos 5 testes E2E cobrindo os fluxos acima
3. Todos os testes passam em modo headless
4. Testes executados em CI (GitHub Actions ou local)
5. Screenshots e vídeos em caso de falha

## Riscos (Hostile Analysis)
- Testes flaky por timing → mitigação: `page.waitForResponse`, `expect.poll`, timeouts adequados
- Seletores frágeis → mitigação: `data-testid` atributos estáveis
- Dependência de estado da base de dados → mitigação: seed de dados antes de cada teste
- Solver demora muito em E2E → mitigação: mock do solver ou instância pequena

## Fase atual
Plan → Verify.
