import path from "node:path";
import { expect, test } from "@playwright/test";

import { accounts, authSession, overview, settings, upstreamProxyAdmin } from "../screenshots/fixtures";
import { createRequestLogEntry, createRequestLogFilterOptions, createRequestLogsResponse, createTelemetryConsent } from "../src/test/mocks/factories";

const before = process.env.OBSERVABILITY_STAGE === "before";
const upstreams = [
  { id: "subscription_pool", type: "subscription_pool", displayName: null, modelSourceKind: null, isDeleted: false },
  { id: "src-a", type: "model_source", displayName: "Same name", modelSourceKind: "openai_compatible", isDeleted: false },
  { id: "src-b", type: "model_source", displayName: "Same name", modelSourceKind: "openai_compatible", isDeleted: false },
  { id: "src-gone", type: "model_source", displayName: null, modelSourceKind: "openai_compatible", isDeleted: true },
];

for (const width of [375, 768, 1440]) {
  test(`upstream selection and heatmap at ${width}px`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const activityRequests: string[] = [];
    const lists: URLSearchParams[] = [];
    await page.setViewportSize({ width, height: 1100 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.addInitScript(() => {
      localStorage.setItem("codex-lb-language", "en");
      localStorage.setItem("codex-lb-theme", "dark");
    });
    await page.route("**/api/**", async (route) => {
      const url = new URL(route.request().url());
      let data: unknown = {};
      if (url.pathname === "/api/dashboard-auth/session") data = authSession;
      else if (url.pathname === "/api/settings/telemetry") data = createTelemetryConsent({ state: "disabled", source: "persisted", active: false });
      else if (url.pathname === "/api/accounts") data = { accounts };
      else if (url.pathname === "/api/dashboard/overview") data = overview;
      else if (url.pathname === "/api/dashboard/projections") data = { depletionPrimary: null, depletionSecondary: null, weeklyCreditPace: null };
      else if (url.pathname === "/api/dashboard/request-activity") {
        activityRequests.push(url.pathname);
        data = { startDate: "2026-05-01", endDate: "2026-10-14", days: Array.from({ length: 167 }, (_, i) => ({ date: new Date(Date.UTC(2026, 4, 1 + i)).toISOString().slice(0, 10), requests: i % 13 })) };
      }
      else if (url.pathname === "/api/settings") data = settings;
      else if (url.pathname === "/api/settings/upstream-proxy") data = upstreamProxyAdmin;
      else if (url.pathname === "/api/request-logs/options") data = { ...createRequestLogFilterOptions(), upstreams };
      else if (url.pathname === "/api/request-logs") {
        lists.push(url.searchParams);
        data = createRequestLogsResponse([createRequestLogEntry({ requestId: "source-request", accountId: null, modelSourceId: "src-gone", modelSourceKind: "openai_compatible" })], 1, false);
      }
      else if (url.pathname.endsWith("/trends")) data = { primary: [], secondary: [], requests: [], tokens: [] };
      await route.fulfill({ json: data });
    });
    await page.route("**/health/ready", (route) => route.fulfill({ json: { status: "ok" } }));
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: "Dashboard", exact: true })).toBeVisible();
    await expect(page.getByRole("cell").filter({ hasText: "src-gone" }).first()).toBeVisible();
    expect(activityRequests).toHaveLength(0);
    if (before) {
      await expect(page.getByRole("button", { name: "Upstream", exact: true })).toHaveCount(0);
    } else {
      await page.getByRole("button", { name: "Upstream", exact: true }).click();
      await expect(page.getByRole("menuitemcheckbox", { name: "Same name · src-a" })).toBeVisible();
      await expect(page.getByRole("menuitemcheckbox", { name: "Same name · src-b" })).toBeVisible();
      await page.getByRole("menuitemcheckbox", { name: "Deleted model source · src-gone" }).click();
      await page.keyboard.press("Escape");
      await expect(page).toHaveURL(/upstream=src-gone/);
      await page.reload();
      await expect(page.getByRole("button", { name: "Deleted model source · src-gone" })).toBeVisible();
      expect(lists.at(-1)?.getAll("upstream")).toEqual(["src-gone"]);
      await page.getByRole("button", { name: "Reset", exact: true }).click();
      await expect(page).not.toHaveURL(/upstream=/);
      await page.goto("/settings");
      await page.getByRole("button", { name: "Request heatmap", exact: true }).click();
      await page.goto("/dashboard");
      await expect(page.getByRole("region", { name: "Request activity · six months" })).toBeVisible();
      await expect(page.getByRole("button", { name: /2026-10-14.*requests/ })).toBeVisible();
      expect(activityRequests.length).toBeGreaterThan(0);
      await page.reload();
      await expect(page.getByRole("region", { name: "Request activity · six months" })).toBeVisible();
    }
    await page.screenshot({ path: path.join(process.env.OBSERVABILITY_EVIDENCE_DIR!, `${before ? "before" : "after"}-${width}.png`), fullPage: true });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(errors).toEqual([]);
  });
}
