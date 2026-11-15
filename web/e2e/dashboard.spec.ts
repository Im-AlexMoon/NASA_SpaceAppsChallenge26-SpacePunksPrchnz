import { test, expect } from "@playwright/test";
test("all migrated routes render and unavailable states stay explicit", async ({
  page,
}) => {
  for (const route of [
    "",
    "mission",
    "investigations",
    "compare",
    "insights",
    "habitat",
    "ask",
    "methods",
  ]) {
    await page.goto("/" + route);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(page.getByRole("navigation")).toBeVisible();
  }
  await page.goto("/ask");
  await page.route("**/api/backend/**", (route) =>
    route.fulfill({ status: 503, body: "Unavailable" }),
  );
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  await expect(page.locator('main [role="alert"]')).toContainText("503");
});
test("evidence mode renders scoped tables and quotations without executing markup", async ({
  page,
}) => {
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
          sources: [
            {
              source_id: "source-1",
              title: "Burn duration",
              review_status: "repository_definition",
              locator: "dictionary#gas_flame_tests",
              sha256: "fixture",
            },
          ],
          chunks: [
            {
              chunk_id: "chunk-1",
              source_id: "source-1",
              section: "Definition",
              text: "<script>not executable</script> burn_time_s: seconds; flow termination differs from natural extinction.",
            },
          ],
        },
      },
    });
  });
  await page.goto("/ask");
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  await expect(page.getByText("SAMPLE", { exact: true })).toBeVisible();
  await page.getByText("Evidence 1: Burn duration").click();
  await expect(page.locator(".excerpt")).toContainText(
    "<script>not executable</script>",
  );
  await page.screenshot({
    path: "../artifacts/rag_ui/desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: "../artifacts/rag_ui/mobile.png",
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
