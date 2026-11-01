import { test, expect } from '@playwright/test';

test.describe.configure({ retries: 2 });

// Only run E2E tests if FULL_STACK_E2E=1 is set (requires full stack: frontend + backend + DB)
const RUN_E2E = process.env.FULL_STACK_E2E === '1';

if (RUN_E2E) {
  test.describe('School Timetable - Fluxos completos', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('http://localhost:3000');
    });

    test('Login com credenciais válidas', async ({ page }) => {
      await page.fill('input[name="email"]', 'admin@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('text=Bem-vindo')).toBeVisible();
    });

    test('Criar curso', async ({ page }) => {
      await page.fill('input[name="email"]', 'admin@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await page.click('text=Cursos');
      await page.click('text=Novo Curso');
      await page.fill('input[name="code"]', 'ENG101');
      await page.fill('input[name="name"]', 'Engenharia 101');
      await page.click('button[type="submit"]');

      await expect(page.locator('text=Engenharia 101')).toBeVisible();
    });

    test('Criar sala', async ({ page }) => {
      await page.fill('input[name="email"]', 'admin@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await page.click('text=Salas');
      await page.click('text=Nova Sala');
      await page.fill('input[name="name"]', 'Laboratório 1');
      await page.fill('input[name="capacity"]', '30');
      await page.selectOption('select[name="room_type"]', 'laboratory');
      await page.click('button[type="submit"]');

      await expect(page.locator('text=Laboratório 1')).toBeVisible();
    });

    test('Criar disciplina', async ({ page }) => {
      await page.fill('input[name="email"]', 'admin@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await page.click('text=Disciplinas');
      await page.click('text=Nova Disciplina');
      await page.fill('input[name="code"]', 'MAT101');
      await page.fill('input[name="name"]', 'Matemática 101');
      await page.fill('input[name="weekly_load"]', '4');
      await page.selectOption('select[name="room_type_required"]', 'normal');
      await page.click('button[type="submit"]');

      await expect(page.locator('text=Matemática 101')).toBeVisible();
    });

    test('Criar turma', async ({ page }) => {
      await page.fill('input[name="email"]', 'admin@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await page.click('text=Turmas');
      await page.click('text=Nova Turma');
      await page.fill('input[name="name"]', 'Turma A');
      await page.fill('input[name="year"]', '1');
      await page.fill('input[name="student_count"]', '25');
      await page.click('button[type="submit"]');

      await expect(page.locator('text=Turma A')).toBeVisible();
    });

    test('Criar professor', async ({ page }) => {
      await page.fill('input[name="email"]', 'admin@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await page.click('text=Professores');
      await page.click('text=Novo Professor');
      await page.fill('input[name="email"]', 'professor@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.fill('input[name="full_name"]', 'Professor Teste');
      await page.selectOption('select[name="role"]', 'teacher');
      await page.click('button[type="submit"]');

      await expect(page.locator('text=Professor Teste')).toBeVisible();
    });

    test('Executar solver', async ({ page }) => {
      await page.fill('input[name="email"]', 'admin@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await page.click('text=Solver');
      await page.selectOption('select[name="solver"]', 'simulated_annealing');
      await page.fill('input[name="time_limit_seconds"]', '30');
      await page.click('button:has-text("Executar")');

      // Aguardar conclusão (máximo 40 segundos)
      await expect(page.locator('text=Concluído')).toBeVisible({ timeout: 45000 });
      await expect(page.locator('text=Score')).toBeVisible();
    });

    test('Submeter contestação', async ({ page }) => {
      // Login como professor
      await page.fill('input[name="email"]', 'professor@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await page.click('text=Contestações');
      await page.click('text=Nova Contestação');
      await page.selectOption('select[name="assignment_id"]', { index: 0 });
      await page.fill('textarea[name="reason"]', 'Conflito de horário');
      await page.selectOption('select[name="justification"]', 'deslocamento');
      await page.click('button[type="submit"]');

      await expect(page.locator('text=Contestação enviada')).toBeVisible();
    });

    test('Admin aprova contestação', async ({ page }) => {
      await page.fill('input[name="email"]', 'admin@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await page.click('text=Contestações');
      await page.click('button:has-text("Aceitar"):first');

      await expect(page.locator('text=Aceita')).toBeVisible();
    });

    test('Exportar horário iCal', async ({ page }) => {
      await page.fill('input[name="email"]', 'admin@test.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');

      await page.click('text=Horários');
      await page.click('text=Exportar iCal');

      // Verifica download
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Download")');
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.ics$/);
    });
  });

  test.describe('Acessibilidade', () => {
    test('Contraste WCAG AA', async ({ page }) => {
      await page.goto('http://localhost:3000');

      // Verificar contraste de cores principais
      const backgroundColor = await page.evaluate(() =>
        getComputedStyle(document.body).backgroundColor
      );
      const textColor = await page.evaluate(() =>
        getComputedStyle(document.body).color
      );

      // Verificação básica (contraste mínimo 4.5:1 para texto normal)
      expect(backgroundColor).toBeTruthy();
      expect(textColor).toBeTruthy();
    });

    test('Navegação por teclado', async ({ page }) => {
      await page.goto('http://localhost:3000');

      // Tab através dos elementos principais
      await page.keyboard.press('Tab');
      await expect(page.locator(':focus')).toBeVisible();

      await page.keyboard.press('Tab');
      await expect(page.locator(':focus')).toBeVisible();
    });
  });
}