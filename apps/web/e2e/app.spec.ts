import { expect, test } from "@playwright/test";

test("landing page launches sample decision", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Hxrizxn AI" })).toBeVisible();
  await page.getByRole("button", { name: /Try Sample Decision/i }).first().click();
  await expect(page.getByText(/Scenario Comparison/i)).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("heading", { name: /Evidence-Building Base Case/i })).toBeVisible();
});
