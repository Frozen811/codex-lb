import path from "node:path";
import { expect, test } from "@playwright/test";

import { accounts, authSession, overview, settings, upstreamProxyAdmin } from "../screenshots/fixtures";
import { createRequestLogFilterOptions, createRequestLogsResponse, createTelemetryConsent } from "../src/test/mocks/factories";

const before = process.env.QUOTA_STAGE === "before";
const estimates = [
  { accountId: "synthetic-pro", observedSince: "2026-10-14T10:00:00Z", observedUntil: "2026-10-14T12:00:00Z",
    observedUsedPercent: 10, observedCostUsd: 4, estimatedFullWeeklyLimitCostUsd: 40 },
  { accountId: "synthetic-lite", observedSince: "2026-10-14T10:00:00Z", observedUntil: "2026-10-14T12:00:00Z",
    observedUsedPercent: 10, observedCostUsd: 12, estimatedFullWeeklyLimitCostUsd: 120 },
];
const pace = {
  creditsAreEstimates: true, proWeeklyCapacityCredits: 36000, accountCostEstimates: estimates,
  totalFullCredits: 45000, totalActualRemainingCredits: 9000, totalExpectedRemainingCredits: 20000,
  actualUsedPercent: 80, scheduledUsedPercent: 55, deltaPercent: 25, scheduleGapCredits: 11000,
  overPlanCredits: 11000, projectedShortfallCredits: 0, pauseForBreakEvenHours: null, paceMultiplier: null,
  throttleToPercent: null, reduceByPercent: null, proAccountEquivalentToCoverOverPlan: null,
  proAccountsToCoverOverPlan: null, projectedDepletionHours: null, projectedMinimumRemainingCredits: null,
  forecastBurnRateCreditsPerHour: 1000, scheduledBurnRateCreditsPerHour: 500,
  headroomPercent: 20, headroomCredits: 9000, burnRateRecentCreditsPerHour: 1000, depletionEtaHours: 9,
  nextReliefInHours: 24, nextReliefCredits: 36000, resetEvents: [], runwayStatus: "tight",
  saturatedAccountCount: 0, topApiKeys: [], addProAccounts: null, status: "ahead", accountCount: 2,
  staleAccountCount: 0, inactiveAccountCount: 0, confidence: "high",
  estimatedFullWeeklyLimitCostUsd: 4699.33, usedCostUsd: 2014,
};

for (const width of [375, 768, 1440]) {
  test(`per-account estimates fit at ${width}px`, async ({ page }) => {
    const visibleEstimates = width === 768 ? [...estimates, ...Array.from({ length: 99 }, (_, i) => ({
      ...estimates[0], accountId: `synthetic-extra-${i}`,
    }))] : estimates;
    const casePace = { ...pace, accountCostEstimates: visibleEstimates };
    await page.setViewportSize({ width, height: 1100 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.addInitScript(() => {
      localStorage.setItem("codex-lb-language", "en");
      localStorage.setItem("codex-lb-theme", "dark");
    });
    await page.route("**/api/**", async (route) => {
      const pathname = new URL(route.request().url()).pathname;
      let data: unknown = {};
      if (pathname === "/api/dashboard-auth/session") data = authSession;
      else if (pathname === "/api/settings/telemetry") data = createTelemetryConsent({ state: "disabled", source: "persisted", active: false });
      else if (pathname === "/api/accounts") data = { accounts };
      else if (pathname === "/api/dashboard/overview") data = { ...overview, weeklyCreditPace: casePace };
      else if (pathname === "/api/dashboard/projections") data = { depletionPrimary: null, depletionSecondary: null, weeklyCreditPace: casePace };
      else if (pathname === "/api/settings") data = settings;
      else if (pathname === "/api/settings/upstream-proxy") data = upstreamProxyAdmin;
      else if (pathname === "/api/request-logs/options") data = createRequestLogFilterOptions();
      else if (pathname === "/api/request-logs") data = createRequestLogsResponse([], 0, false);
      else if (pathname.endsWith("/trends")) data = { primary: [], secondary: [], requests: [], tokens: [] };
      await route.fulfill({ json: data });
    });
    await page.route("**/health/ready", (route) => route.fulfill({ json: { status: "ok" } }));
    await page.goto("/dashboard");
    const rows = page.getByTestId("weekly-estimated-limit-cost");
    await expect(rows).toHaveCount(before ? 1 : visibleEstimates.length);
    if (before) await expect(rows).toContainText("$4,699.33");
    else {
      await expect(rows.filter({ hasText: "synthetic-pro" })).toContainText("$40.00");
      await expect(rows.filter({ hasText: "synthetic-lite" })).toContainText("$120.00");
      await expect(page.getByText("Credits are estimates; upstream percentages and reset times determine availability.")).toBeVisible();
      await expect(page.getByText(/\$4,699.33/)).toHaveCount(0);
      await expect(page.getByText(/Not a guaranteed allowance/)).toHaveCount(visibleEstimates.length);
      if (width === 768) {
        const list = page.getByTestId("weekly-cost-estimates");
        expect(await list.evaluate((element) => element.scrollHeight > element.clientHeight)).toBe(true);
        expect(await list.evaluate((element) => element.clientHeight)).toBeLessThanOrEqual(160);
        await rows.last().scrollIntoViewIfNeeded();
        await expect(rows.last()).toBeVisible();
        await list.evaluate((element) => { element.scrollTop = 0; });
      }
    }
    await rows.first().scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(process.env.QUOTA_EVIDENCE_DIR!, `${before ? "before" : "after"}-${width}.png`), fullPage: true });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  });
}
