# AES Plan Spec — T027 Testes E2E Playwright

## 1. Sumário Executivo
Testes end-to-end com Playwright para validar fluxos completos da plataforma web no browser real.

## 2. Stack
- Playwright (Node.js)
- `playwright.config.ts`
- Testes em TypeScript
- Page Objects para reutilização de seletores

## 3. Testes a Implementar
### T1: Fluxo Docente Completo
1. Login como docente
2. Aceder ao calendário de indisponibilidades
3. Marcar um slot como indisponível com justificação "deslocamento"
4. Ver o slot marcado no calendário
5. Ver o horário atribuído (sem o slot indisponível)
6. Submeter contestação de um slot atribuído
7. Ver a contestação na lista (estado: pendente)

### T2: Fluxo Admin Completo
1. Login como admin
2. Aceder à gestão de utilizadores → criar um docente
3. Aceder à gestão de salas → criar uma sala de laboratório
4. Gerar horário (clicar botão "Gerar Horário")
5. Aguardar conclusão do solver
6. Ver horário gerado na tabela
7. Aceder às contestações pendentes
8. Aceitar uma contestação
9. Verificar que o horário foi reexecutado e atualizado

### T3: Fluxo Estudante
1. Login como estudante
2. Ver horário da sua turma
3. Verificar que as aulas estão corretas (sem conflitos)

### T4: Acessibilidade Básica
1. Navegação por teclado (Tab) nas principais páginas
2. Contraste de cores nos elementos interativos (verificação manual ou automatizada parcial)

### T5: Responsividade
1. Abrir a aplicação em largura mobile (375px)
2. Verificar que o menu hamburger aparece
3. Verificar que a tabela de horário se adapta

## 4. Page Objects
- `e2e/pages/LoginPage.ts`
- `e2e/pages/CalendarPage.ts`
- `e2e/pages/SchedulePage.ts`
- `e2e/pages/DisputesPage.ts`
- `e2e/pages/AdminDashboardPage.ts`

## 5. Dados de Teste
- Seed de dados de exemplo antes de cada teste (via API ou seed direto na DB)
- Utilizadores de teste: admin@test.com, teacher@test.com, student@test.com

## 6. Critérios de Aceitação
- Todos os 5 testes passam em modo headless
- Screenshots e vídeos gravados em falha
- Testes executados em CI (GitHub Actions)
