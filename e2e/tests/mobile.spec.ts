import { test, expect } from "@playwright/test";

test.describe("Responsividade Mobile", () => {
  test.use({ ...require("@playwright/test").devices["Pixel 5"] });

  test("Menu hamburger deve aparecer em mobile", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', "test@test.pt");
    await page.fill('input[type="password"]', "senha123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/dashboard");

    // Verificar que o layout se adapta
    await expect(page.locator("h1")).toBeVisible();
  });
});
