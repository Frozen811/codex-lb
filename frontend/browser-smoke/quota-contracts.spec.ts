import fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";
import { accounts, authSession, settings, upstreamProxyAdmin, models } from "../screenshots/fixtures";

const stage = process.env.QUOTA_STAGE ?? "after";
const evidence = process.env.QUOTA_EVIDENCE_DIR!;
const monthly = JSON.parse(fs.readFileSync(path.join(evidence, `${stage}-payload.json`), "utf8"));

for (const width of [1440, 390]) {
  test(`quota windows and account switching at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.addInitScript(() => {
      localStorage.setItem("codex-lb-language", "en");
      localStorage.setItem("codex-lb-theme", "dark");
    });
    const dual = { ...accounts[0], accountId: "dual-account", email: "dual@example.com", displayName: "dual@example.com" };
    const monthlyAccount = { ...accounts[0], ...monthly };
    await page.route("**/api/**", async (route) => {
      const p = new URL(route.request().url()).pathname;
      let data: unknown = {};
      if (p === "/api/dashboard-auth/session") data = authSession;
      else if (p === "/api/accounts") data = { accounts: [dual, monthlyAccount] };
      else if (p === "/api/settings") data = settings;
      else if (p === "/api/settings/upstream-proxy") data = upstreamProxyAdmin;
      else if (p === "/api/models") data = { models };
      else if (p.endsWith("/usage-reset-credits")) data = {
        accountId: p.split("/").at(-2), rateLimitResetCredits: { availableCount: 0 },
      };
      else if (p.endsWith("/usage")) data = { points: [] };
      else if (p.endsWith("/trends")) {
        data = {
          accountId: p.split("/").at(-2),
          primary: [],
          secondary: [
            { t: "2026-10-05T00:00:00Z", v: 90 },
            { t: "2026-10-06T00:00:00Z", v: 76 },
          ],
          secondaryScheduled: [], requests: [], tokens: [],
        };
      }
      await route.fulfill({ contentType: "application/json", body: JSON.stringify(data) });
    });
    await page.route("**/health/ready", route => route.fulfill({ contentType: "application/json", body: '{"status":"ok"}' }));
    await page.goto("http://127.0.0.1:4183/accounts?selected=dual-account");
    await expect(page.getByText("5h remaining", { exact: true })).toBeVisible();
    await page.evaluate(() => {
      window.history.pushState({}, "", "/accounts?selected=monthly-team");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    if (stage === "after") {
      await expect(page.getByText("Monthly remaining", { exact: true })).toBeVisible();
      await expect(page.getByText("76%", { exact: true }).first()).toBeVisible();
      await expect(page.getByText("5h remaining", { exact: true })).toHaveCount(0);
      await expect(page.getByText("Weekly remaining", { exact: true })).toHaveCount(0);
    } else {
      await expect(page.getByText("Monthly remaining", { exact: true })).toHaveCount(0);
      await expect(page.getByText("Weekly remaining", { exact: true })).toBeVisible();
    }
    await expect(page.locator(".recharts-area").first()).toBeVisible();
    await expect(page.getByText("0 available", { exact: true }).first()).toBeVisible();
    await page.addStyleTag({ content: "*,*::before,*::after{animation:none!important;transition:none!important}" });
    await page.screenshot({ path: path.join(evidence, `${stage}-monthly-${width}.png`), fullPage: true });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.evaluate(() => {
      window.history.pushState({}, "", "/accounts?selected=dual-account");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    await expect(page.getByText("5h remaining", { exact: true })).toBeVisible();
    await expect(page.getByText("Weekly remaining", { exact: true })).toBeVisible();
    await expect(page.getByText("Monthly remaining", { exact: true })).toHaveCount(0);
  });
}
