import path from "node:path";
import { expect, test } from "@playwright/test";
import { accounts, apiKeys, authSession, settings, upstreamProxyAdmin, models } from "../screenshots/fixtures";

const baseURL = process.env.INVENTORY_BASE_URL ?? "http://127.0.0.1:4179";
const stage = process.env.INVENTORY_STAGE ?? "after";
const evidence = process.env.INVENTORY_EVIDENCE_DIR!;

for (const width of [1440, 390]) {
  test(`inventory at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.addInitScript(() => {
      localStorage.setItem("codex-lb-language", "en");
      localStorage.setItem("codex-lb-theme", "dark");
    });
    const syntheticAccounts = accounts.map((account, index) => ({
      ...account,
      availableResetCredits: index === 0 ? 2 : 0,
      resetCreditNearestExpiresAt: new Date(Date.now() + 48 * 3_600_000).toISOString(),
    }));
    await page.route("**/api/**", async (route) => {
      const url = new URL(route.request().url());
      const p = url.pathname;
      let data: unknown = {};
      if (p === "/api/dashboard-auth/session") data = authSession;
      else if (p === "/api/accounts") data = { accounts: syntheticAccounts };
      else if (p === "/api/settings") data = settings;
      else if (p === "/api/settings/upstream-proxy") data = upstreamProxyAdmin;
      else if (p === "/api/api-keys" || p === "/api/api-keys/") data = apiKeys;
      else if (p === "/api/models") data = { models: stage === "after" ? [
        ...models,
        ...["gpt-image-1", "gpt-image-1-mini", "gpt-image-1.5", "gpt-image-2", "gpt-image-2.5-flare", "gpt-image-2.5-sunburst"]
          .map(id => ({ id, name: id, sourceOnly: false, imageOnly: true, supportedReasoningEfforts: [] })),
      ] : models };
      else if (p.endsWith("/usage-reset-credits")) data = { rateLimitResetCredits: { availableCount: 2 } };
      else if (p.endsWith("/usage")) data = { points: [] };
      else if (p.endsWith("/trends")) data = { primary: [], secondary: [], requests: [], tokens: [] };
      await route.fulfill({ contentType: "application/json", body: JSON.stringify(data) });
    });
    await page.route("**/health/ready", (route) => route.fulfill({ contentType: "application/json", body: '{"status":"ok"}' }));
    await page.goto(`${baseURL}/accounts`);
    await expect(page.getByRole("heading", { name: "Accounts", exact: true })).toBeVisible();
    await expect(page.getByTestId("accounts-layout")).toBeVisible();
    if (stage === "after") {
      await expect(page.getByTestId("accounts-distribution-charts")).toBeVisible();
      await expect(page.locator('[data-testid="accounts-distribution-charts"] .recharts-pie-sector').first()).toBeVisible();
      await expect(page.getByRole("img", { name: /expires within 3 days/i })).toBeVisible();
    }
    await page.addStyleTag({ content: "*,*::before,*::after{animation:none!important;transition:none!important}" });
    await page.screenshot({ path: path.join(evidence, `${stage}-accounts-${width}.png`), fullPage: true });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    if (stage === "after") {
      await page.getByTestId("account-list-scroll-region").getByRole("button").first().click();
      const selected = new URL(page.url()).searchParams.get("selected");
      await page.getByTestId("accounts-list-card").getByRole("combobox").nth(1).click();
      await expect(page.getByRole("option", { name: "Monthly quota (highest remaining)" })).toBeVisible();
      await page.getByRole("option", { name: "Monthly quota (highest remaining)" }).click();
      expect(new URL(page.url()).searchParams.get("selected")).toBe(selected);
      await page.screenshot({ path: path.join(evidence, `${stage}-accounts-sort-${width}.png`), fullPage: true });
    }
    await page.evaluate(() => {
      window.history.pushState({}, "", "/apis");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    await expect(page.getByRole("heading", { name: "APIs", exact: true })).toBeVisible();
    await expect(page.getByText(apiKeys[0].name).first()).toBeVisible();
    await page.screenshot({ path: path.join(evidence, `${stage}-apis-${width}.png`), fullPage: true });
    if (stage === "after") {
      await page.getByRole("button", { name: "List view", exact: true }).click();
      if (width >= 1024) await expect(page.getByRole("button", { name: /last used/i })).toBeVisible();
      else await expect(page.getByRole("combobox", { name: "Sort API keys" })).toBeVisible();
      await page.screenshot({ path: path.join(evidence, `${stage}-apis-list-${width}.png`), fullPage: true });
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.getByRole("button", { name: "Create API Key", exact: true }).click();
    await page.getByRole("button", { name: "All models", exact: true }).click();
    if (stage === "after") await expect(page.getByRole("menuitemcheckbox", { name: "gpt-image-2", exact: true })).toBeVisible();
    await page.screenshot({ path: path.join(evidence, `${stage}-image-picker-${width}.png`), fullPage: true });
  });
}
