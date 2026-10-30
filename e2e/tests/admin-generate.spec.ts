import { test, expect } from "@playwright/test";

test.describe("Fluxo Admin — Gerar Horário", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', "admin@escola.pt");
    await page.fill('input[type="password"]', "senha123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/dashboard");
  });

  test("Deve gerar horário com sucesso", async ({ page }) => {
    // Clicar em "Gerar Horário"
    await page.click('button:has-text("Gerar Horário")');

    // Aguardar processamento
    await page.waitForSelector('text=Horário gerado com sucesso', { timeout: 60000 });

    // Verificar que não há conflitos
    await expect(page.locator('text=Viável')).toBeVisible();
  });
});
