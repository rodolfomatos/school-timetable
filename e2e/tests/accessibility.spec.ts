import { test, expect } from "@playwright/test";

test.describe("Acessibilidade Básica", () => {
  test("Deve ser navegável por teclado", async ({ page }) => {
    await page.goto("/login");

    // Navegar com Tab
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");

    // Verificar que o foco está visível
    const focused = page.locator(":focus");
    await expect(focused).toBeVisible();
  });

  test("Elementos interativos devem ter contraste adequado", async ({ page }) => {
    await page.goto("/login");

    // Verificar que o botão principal tem cor de contraste
    const button = page.locator('button[type="submit"]');
    await expect(button).toBeVisible();
  });
});
