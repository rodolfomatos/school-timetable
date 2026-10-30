import { test, expect } from "@playwright/test";

test.describe("Fluxo de Contestações", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', "professor@escola.pt");
    await page.fill('input[type="password"]', "senha123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/dashboard");
  });

  test("Docente deve conseguir contestar um slot atribuído", async ({ page }) => {
    // Navegar para o horário
    await page.click('text=Ver Horário');
    await expect(page).toHaveURL("/schedule");

    // Clicar em uma aula para contestar
    await page.click('text=Aula');

    // Preencher o formulário de contestação
    await page.fill('textarea', "Não posso ter esta aula neste horário");
    await page.selectOption('select', { label: "Deslocamento entre instituições" });

    // Submeter
    await page.click('button:has-text("Submeter Contestação")');

    // Verificar que a contestação foi submetida
    await expect(page.locator('text=Contestação submetida com sucesso')).toBeVisible();
  });
});
