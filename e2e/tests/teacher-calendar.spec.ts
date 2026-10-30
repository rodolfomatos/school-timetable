import { test, expect } from "@playwright/test";

test.describe("Fluxo Docente — Marcar Indisponibilidade", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    // Login como docente (mock - em produção usaria credenciais reais)
    await page.fill('input[type="email"]', "professor@escola.pt");
    await page.fill('input[type="password"]', "senha123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/dashboard");
  });

  test("Deve marcar um slot como indisponível com justificação", async ({ page }) => {
    // Navegar para o calendário do docente
    await page.click('text=Minhas Restrições');
    await expect(page).toHaveURL("/teacher/calendar");

    // Clicar em um slot (segunda-feira, hora 1)
    await page.click('text=segunda');

    // Selecionar justificação
    await page.selectOption('select', { label: "Deslocamento entre instituições" });

    // Guardar
    await page.click('button:has-text("Guardar")');

    // Verificar que o slot está marcado como indisponível
    await expect(page.locator('text=✕')).toBeVisible();
  });
});
