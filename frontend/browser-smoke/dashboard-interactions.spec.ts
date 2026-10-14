import path from "node:path";
import { expect, test, type Page } from "@playwright/test";

import { accounts, authSession, overview, settings, upstreamProxyAdmin } from "../screenshots/fixtures";
import {
  createDashboardProjections,
  createRequestLogFilterOptions,
  createRequestLogsResponse,
  createTelemetryConsent,
} from "../src/test/mocks/factories";

const evidence = process.env.INTERACTIONS_EVIDENCE_DIR!;
const before = process.env.INTERACTIONS_STAGE === "before";
const syntheticAccounts = Array.from({ length: 31 }, (_, index) => ({
  ...accounts[index % accounts.length],
  accountId: `synthetic-${index}`,
  displayName: `${String(31 - index).padStart(2, "0")}-${"long-account-name-".repeat(12)}`,
  email: `${"long-email-".repeat(12)}${index}@example.invalid`,
  availableResetCredits: 3,
}));

async function installFixtures(page: Page, options: { totp?: boolean; consent?: boolean } = {}) {
  let verified = !options.totp;
  let decisions = 0;
  let telemetryReads = 0;
  const codes: unknown[] = [];
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.addInitScript(() => {
    localStorage.setItem("codex-lb-language", "en");
    localStorage.setItem("codex-lb-theme", "dark");
  });
  await page.route("**/api/**", async (route) => {
    const p = new URL(route.request().url()).pathname;
    let data: unknown = {};
    if (p === "/api/dashboard-auth/session") data = verified
      ? authSession
      : { ...authSession, authenticated: false, totpRequiredOnLogin: true };
    else if (p === "/api/dashboard-auth/totp/verify") {
      codes.push(route.request().postDataJSON());
      verified = true;
      data = authSession;
    } else if (p === "/api/settings/telemetry") {
      if (route.request().method() === "PUT") {
        decisions++;
        if (decisions === 1) {
          await route.fulfill({ status: 503, json: { error: { code: "save_failed", message: "Consent save unavailable" } } });
          return;
        }
      } else telemetryReads++;
      data = createTelemetryConsent({ state: options.consent && decisions < 2 ? "undecided" : "disabled", source: options.consent && decisions < 2 ? "default" : "persisted", active: !!options.consent && decisions < 2 });
    } else if (p === "/api/accounts") data = { accounts: syntheticAccounts };
    else if (p === "/api/dashboard/overview") data = { ...overview, accounts: syntheticAccounts };
    else if (p === "/api/dashboard/projections") data = createDashboardProjections();
    else if (p === "/api/settings") data = { ...settings, dashboardSessionTtlSeconds: 31_536_000 };
    else if (p === "/api/settings/upstream-proxy") data = upstreamProxyAdmin;
    else if (p === "/api/request-logs/options") data = createRequestLogFilterOptions();
    else if (p === "/api/request-logs") data = createRequestLogsResponse([], 0, false);
    else if (p.endsWith("/trends")) data = { primary: [], secondary: [], requests: [], tokens: [] };
    else if (p.endsWith("/usage")) data = { points: [] };
    await route.fulfill({ json: data });
  });
  await page.route("**/health/ready", (route) => route.fulfill({ json: { status: "ok" } }));
  return { codes, decisions: () => decisions, telemetryReads: () => telemetryReads };
}

async function capture(page: Page, name: string) {
  await page.screenshot({ path: path.join(evidence, `${before ? "before" : "after"}-${name}.png`), fullPage: true });
}

for (const width of [320, 768, 1440]) {
  test(`account list remains contained at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await installFixtures(page);
    await page.goto("/accounts");
    const region = page.getByTestId("account-list-scroll-region");
    await expect(region.getByRole("button")).toHaveCount(31);
    await capture(page, `accounts-${width}`);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(await region.evaluate((element) => element.scrollHeight > element.clientHeight)).toBe(true);
    await region.getByRole("button").last().click();
    await expect(page).toHaveURL(/selected=synthetic-/);
    await expect(page.getByTestId("accounts-list-card").getByRole("button", { name: "Add account", exact: true })).toBeVisible();
  });
}

test("Compact sorting, persistence and fullscreen preserve the other URL filters", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await installFixtures(page);
  await page.goto("/dashboard?overviewTimeframe=1d");
  await page.getByRole("radio", { name: before ? "dashboard.accounts.viewCompact" : "View accounts in compact tables" }).click();
  const compact = page.getByTestId("dashboard-account-compact");
  await expect(compact).toBeVisible();
  const columns = compact.locator(".rounded-b-lg");
  const order = () => columns.evaluateAll((items) => items.map((item) => Array.from(item.querySelectorAll('button')).map((button) => button.textContent)));
  const originalOrder = await order();
  const members = originalOrder.map((column) => [...column].sort());
  const mountedRows = await compact.getByTestId("account-compact-row").elementHandles();
  const header = compact.getByRole("button", { name: "Account", exact: true }).first();
  await header.click();
  expect(await order()).toEqual(members);
  await compact.getByRole("button", { name: "Account, sorted ascending" }).first().click();
  expect(await order()).toEqual(members.map((column) => [...column].reverse()));
  await compact.getByRole("button", { name: "Account, sorted descending" }).first().click();
  expect(await order()).toEqual(originalOrder);
  expect(await Promise.all(mountedRows.map((row) => row.evaluate((element) => element.isConnected)))).toEqual(Array(31).fill(true));
  expect(await page.evaluate(() => localStorage.getItem("codex-lb-dashboard-account-list-sort"))).toBeNull();
  await page.getByRole("button", { name: before ? "dashboard.accounts.viewFullscreen" : "Full screen", exact: true }).click();
  await expect(page).toHaveURL(/accountsFullscreen=1/);
  await capture(page, "compact-fullscreen");
  await page.reload();
  await expect(page.getByTestId("dashboard-account-compact")).toBeVisible();
  await page.getByRole("button", { name: before ? "dashboard.accounts.viewFullscreen" : "Exit full screen", exact: true }).click();
  expect(new URL(page.url()).searchParams.get("accountsFullscreen")).toBeNull();
  expect(new URL(page.url()).searchParams.get("overviewTimeframe")).toBe("1d");
  expect(await page.evaluate(() => localStorage.getItem("codex-lb-dashboard-account-view-mode"))).toBe("compact");
});

test("native OTP replacement input survives an outside interaction and submits exactly once", async ({ page }) => {
  const state = await installFixtures(page, { totp: true });
  await page.goto("/");
  const input = page.getByLabel("TOTP code");
  await expect(input).toHaveAttribute("autocomplete", "one-time-code");
  await expect(input).toHaveAttribute("inputmode", "numeric");
  await page.mouse.click(2, 2);
  await expect(page.getByRole("dialog")).toBeVisible();
  await capture(page, "totp");
  await input.evaluate((element: HTMLInputElement) => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")!.set!.call(element, "234567");
    element.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertReplacementText", data: "234567" }));
  });
  await expect(page.getByRole("dialog")).toBeHidden();
  expect(state.codes).toEqual([{ code: "234567" }]);
});

test("consent failure, retry and browser dismissal", async ({ page }) => {
  const state = await installFixtures(page, { consent: true });
  await page.goto("/");
  const dialog = page.getByRole("dialog", { name: "Anonymous telemetry" });
  await expect(dialog).toBeVisible();
  await expect(dialog.locator("pre")).toBeHidden();
  const disable = dialog.getByRole("button", { name: "Disable telemetry" });
  expect(await disable.getAttribute("class")).toBe(await dialog.getByRole("button", { name: "Keep enabled" }).getAttribute("class"));
  await disable.click();
  await expect.poll(state.decisions).toBe(1);
  if (!before) await expect(dialog.getByText("Consent save unavailable")).toBeVisible();
  await capture(page, "consent-error");
  expect(await page.evaluate(() => localStorage.getItem("codex-lb.telemetry-consent-dismissed"))).toBeNull();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  const reads = state.telemetryReads();
  await page.reload();
  await expect(page.getByRole("heading", { name: "Dashboard", exact: true })).toBeVisible();
  await expect(dialog).toBeHidden();
  expect(state.telemetryReads()).toBe(reads);
  expect(state.decisions()).toBe(1);
  await page.evaluate(() => localStorage.removeItem("codex-lb.telemetry-consent-dismissed"));
  await page.reload();
  await dialog.getByRole("button", { name: "Disable telemetry" }).click();
  await expect(dialog).toBeHidden();
  expect(state.decisions()).toBe(2);
});

test("session setting explains long-session locality without changing the stored value", async ({ page }) => {
  await installFixtures(page);
  await page.goto("/settings#access");
  const input = page.getByRole("spinbutton", { name: "Dashboard session lifetime" });
  await expect(input).toHaveValue("8760");
  if (!before) await expect(page.getByText(/LAN, remote or proxy access normally uses a 12-hour session/)).toBeVisible();
  await input.scrollIntoViewIfNeeded();
  await capture(page, "session-policy");
});
