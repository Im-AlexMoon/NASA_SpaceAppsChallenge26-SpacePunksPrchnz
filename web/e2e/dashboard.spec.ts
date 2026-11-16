import { test, expect } from "@playwright/test";

const routes = ["", "atmosphere", "findings", "gaps", "investigations", "ask", "methods"];

test("every page renders with one h1 and the main navigation", async ({ page }) => {
  for (const route of routes) {
    await page.goto("/" + route);
    await expect(page.getByRole("heading", { level: 1 })).toHaveCount(1);
    await expect(page.getByRole("navigation", { name: "Main" })).toBeAttached();
  }
});

test("atmosphere explorer shows tiers and never invents a number at tier C", async ({ page }) => {
  await page.goto("/atmosphere");
  await expect(page.getByText("Model interpolation").first()).toBeVisible();
  await page.getByRole("button", { name: /ISS cabin/ }).click();
  await expect(page.getByText("Measured nearby").first()).toBeVisible();
  await page.getByRole("button", { name: /Spacesuit/ }).click();
  await expect(page.getByText("No model reading")).toBeVisible();
  await page.getByRole("button", { name: /Lunar base/ }).click();
  await expect(page.getByRole("note")).toContainText("do not establish");
});

test("ranking reorders when the profile changes", async ({ page }) => {
  await page.goto("/investigations");
  const first = page.locator(".rank-list > li").first();
  const before = await first.getAttribute("data-id");
  await page.getByRole("button", { name: "Detection researcher" }).click();
  await expect(first).not.toHaveAttribute("data-id", before!);
});

test("ask keeps unavailable states explicit", async ({ page }) => {
  await page.goto("/ask");
  await page.route("**/api/backend/**", (route) => route.fulfill({ status: 503, body: "Unavailable" }));
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  await expect(page.locator('main [role="alert"]')).toContainText("503");
});

test("evidence mode renders quotations without executing markup", async ({ page }) => {
  await page.route("**/api/backend/chat", (route) => {
    expect(route.request().postDataJSON().evidence_only).toBe(true);
    return route.fulfill({
      json: {
        status: "partial",
        language: "en",
        message: "Retrieved evidence",
        claims: [],
        usage_tokens: 0,
        evidence: {
          build_id: "fixture-build",
          source_mode: "sample",
          tools: [],
          sources: [{ source_id: "source-1", title: "Burn duration", review_status: "repository_definition", locator: "dictionary#gas_flame_tests", sha256: "fixture" }],
          chunks: [{ chunk_id: "chunk-1", source_id: "source-1", section: "Definition", text: "<script>not executable</script> burn_time_s: seconds." }],
        },
      },
    });
  });
  await page.goto("/ask");
  await page.getByRole("checkbox", { name: /Gemini/ }).uncheck();
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  await expect(page.getByText("SAMPLE", { exact: true })).toBeVisible();
  await page.getByText("Evidence 1: Burn duration").click();
  await expect(page.locator(".excerpt")).toContainText("<script>not executable</script>");
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
