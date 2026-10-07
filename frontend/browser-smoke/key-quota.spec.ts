import fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";
import { authSession, settings, models, accounts, upstreamProxyAdmin, overview } from "../screenshots/fixtures";
import { createApiKey, createApiKeyUsage7Day, createApiKeyTrends } from "../src/test/mocks/factories";

for (const width of [1440, 390]) {
  test(`observation window and display-only credits at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.addInitScript(() => localStorage.setItem("codex-lb-language", "en"));
    const key = createApiKey({ id: "window", name: "Window client", limits: [
      { id: 1, limitType: "credits", limitWindow: "5h", maxValue: 100, currentValue: 0, modelFilter: null,
        resetAt: "2026-11-01T00:00:00Z" },
    ] });
    const requests: string[] = [];
    await page.route("**/api/**", async (route) => {
      const url = new URL(route.request().url());
      requests.push(url.pathname + url.search);
      let data: unknown = {};
      if (url.pathname === "/api/dashboard-auth/session") data = authSession;
      else if (url.pathname === "/api/dashboard/overview") data = overview;
      else if (url.pathname === "/api/settings") data = settings;
      else if (url.pathname === "/api/settings/upstream-proxy") data = upstreamProxyAdmin;
      else if (url.pathname === "/api/accounts") data = { accounts };
      else if (url.pathname === "/api/models") data = { models };
      else if (url.pathname === "/api/api-keys/") data = [key];
      else if ((url.pathname.endsWith("/usage") || url.pathname.endsWith("/usage-7d"))) data = createApiKeyUsage7Day({ keyId: key.id, totalTokens: Number(url.searchParams.get("days") ?? 7) * 100 });
      else if (url.pathname.endsWith("/trends")) data = createApiKeyTrends({ keyId: key.id });
      await route.fulfill({ contentType: "application/json", body: JSON.stringify(data) });
    });
    await page.goto("/");
    await page.addStyleTag({ content: "*, *::before, *::after { animation: none !important; transition: none !important; }" });
    await page.locator('a[href="/apis"]').first().waitFor({ state: "attached" });
    await page.evaluate(() => {
      window.history.pushState({}, "", "/apis");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    if (process.env.KEY_QUOTA_STAGE === "before") {
      await expect(page.getByRole("button", { name: "Actions", exact: true })).toBeVisible();
    } else {
      await page.getByRole("combobox", { name: "Observation window" }).selectOption("30");
      await expect.poll(() => requests.includes("/api/api-keys/window/usage?days=30")).toBe(true);
      await expect.poll(() => requests.includes("/api/api-keys/window/trends?days=30")).toBe(true);
      await expect(page.getByText("30-day token and cost activity")).toBeVisible();
    }
    await expect(page.locator(".recharts-surface").first()).toBeVisible();
    const evidence = process.env.KEY_QUOTA_EVIDENCE_DIR;
    if (evidence) {
      fs.mkdirSync(evidence, { recursive: true });
      await page.screenshot({ path: path.join(evidence, `${process.env.KEY_QUOTA_STAGE ?? "after"}-windows-${width}.png`), fullPage: true });
    }
    await page.getByRole("button", { name: "Actions", exact: true }).click();
    await page.getByRole("menuitem", { name: "Edit", exact: true }).click();
    if (process.env.KEY_QUOTA_STAGE !== "before") {
      const help = page.getByText(/Display only: traffic does not consume these credits/);
      await help.scrollIntoViewIfNeeded();
      await expect(help).toBeVisible();
    } else {
      await page.getByRole("combobox", { name: "Type", exact: true }).scrollIntoViewIfNeeded();
    }
    if (evidence) await page.screenshot({ path: path.join(evidence, `${process.env.KEY_QUOTA_STAGE ?? "after"}-credits-${width}.png`) });
  });
}
