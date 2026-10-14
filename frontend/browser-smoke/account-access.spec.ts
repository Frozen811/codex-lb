import path from "node:path";
import { expect, test } from "@playwright/test";
import { accounts, authSession, settings, upstreamProxyAdmin } from "../screenshots/fixtures";
import { createTelemetryConsent } from "../src/test/mocks/factories";

const stage = process.env.ACCOUNT_ACCESS_STAGE ?? "after";
const evidence = process.env.ACCOUNT_ACCESS_EVIDENCE_DIR!;
const longEmail = `${"long-email-".repeat(25)}@example.invalid`;
const longWorkspace = "workspace-".repeat(50);
const account = { ...accounts[0], accountId: "synthetic-pat", email: longEmail, alias: "Business PAT", displayName: "Business PAT", chatgptAccountId: longWorkspace };

for (const width of [390, 768, 1440]) {
 for (const accessOnly of [true, false]) {
  const mode = accessOnly ? "access-only" : "oauth";
  test(`account identity and ${mode} export at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.addInitScript(() => localStorage.setItem("codex-lb-language", "en"));
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.route("**/health/ready", (route) => route.fulfill({ json: { status: "ok" } }));
    await page.route("**/api/**", async (route) => {
      const endpoint = new URL(route.request().url()).pathname;
      let data: unknown = {};
      if (endpoint === "/api/dashboard-auth/session") data = authSession;
      else if (endpoint === "/api/accounts") data = { accounts: [account] };
      else if (endpoint === "/api/settings") data = settings;
      else if (endpoint === "/api/settings/telemetry") data = createTelemetryConsent({ state: "disabled", source: "persisted", active: false });
      else if (endpoint === "/api/settings/upstream-proxy") data = upstreamProxyAdmin;
      else if (endpoint.endsWith("/usage") || endpoint.endsWith("/trends")) data = { points: [], primary: [], secondary: [], requests: [], tokens: [] };
      else if (endpoint.endsWith("/export/auth")) data = {
        filename: "synthetic-pat.json", account: { accountId: account.accountId, email: longEmail, chatgptAccountId: longWorkspace },
        tokens: { idToken: accessOnly ? null : "synthetic-id", accessToken: "synthetic-access", refreshToken: accessOnly ? null : "synthetic-refresh", expiresAtMs: 0 },
        codexAuthJson: { auth_mode: "chatgpt", OPENAI_API_KEY: null, email: longEmail, plan_type: "team", workspace_id: longWorkspace,
          workspace_label: "Business workspace", seat_type: "standard", last_refresh: "2026-10-14T00:00:00Z",
          tokens: { id_token: accessOnly ? null : "synthetic-id", access_token: "synthetic-access", refresh_token: accessOnly ? null : "synthetic-refresh", account_id: longWorkspace } },
        opencodeAuthJson: { openai: { type: "oauth", access: "synthetic-access", refresh: accessOnly ? "" : "synthetic-refresh", expires: 0, accountId: longWorkspace } },
      };
      await route.fulfill({ json: data });
    });
    await page.goto(`/accounts?selected=${account.accountId}`);
    await page.addStyleTag({ content: "*,*::before,*::after{animation:none!important;transition:none!important}" });
    await expect(page.getByRole("button", { name: "Export", exact: true })).toBeVisible();
    await page.screenshot({ path: path.join(evidence, `${stage}-${mode}-accounts-${width}.png`), fullPage: true });
    const detailOverflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    await page.getByRole("button", { name: "Export", exact: true }).click();
    if (stage === "before") {
      await page.screenshot({ path: path.join(evidence, `${stage}-${mode}-export-${width}.png`), fullPage: true });
      expect(detailOverflow).toBe(false);
    }
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await page.screenshot({ path: path.join(evidence, `${stage}-${mode}-export-${width}.png`), fullPage: true });
    expect(detailOverflow).toBe(false);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(await dialog.evaluate((element) => element.scrollWidth <= element.clientWidth)).toBe(true);
    await expect(dialog.getByRole("button", { name: "Copy access token" })).toBeVisible();
    await expect(dialog.getByRole("button", { name: "Copy refresh token" })).toHaveCount(accessOnly ? 0 : 1);
    const downloadPromise = page.waitForEvent("download");
    await dialog.getByRole("button", { name: "Download", exact: true }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe("auth.json");
    await download.saveAs(path.join(evidence, `synthetic-${mode}-${width}-auth.json`));
    await page.screenshot({ path: path.join(evidence, `${stage}-${mode}-download-${width}.png`) });
    await dialog.getByRole("button", { name: "Close", exact: true }).first().click();
    expect(errors).toEqual([]);
  });
 }
}
