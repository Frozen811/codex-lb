import path from "node:path";
import { expect, test } from "@playwright/test";
import { accounts, authSession, settings, upstreamProxyAdmin } from "../screenshots/fixtures";

const stage = process.env.IMPORT_STAGE ?? "after";
const evidence = process.env.IMPORT_EVIDENCE_DIR!;

for (const width of [1440, 390]) {
  test(`auth import at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.addInitScript(() => localStorage.setItem("codex-lb-language", "en"));
    const sent: string[] = [];
    let releaseFirst: (() => void) | undefined;
    const firstPending = new Promise<void>(resolve => { releaseFirst = resolve; });
    await page.route("**/health/ready", route => route.fulfill({ contentType: "application/json", body: '{"status":"ok"}' }));
    await page.route("**/api/**", async (route) => {
      const p = new URL(route.request().url()).pathname;
      let data: unknown = {};
      if (p === "/api/dashboard-auth/session") data = authSession;
      else if (p === "/api/accounts") data = { accounts };
      else if (p === "/api/settings") data = settings;
      else if (p === "/api/settings/upstream-proxy") data = upstreamProxyAdmin;
      else if (p === "/api/accounts/import") {
        sent.push(route.request().postData() ?? "");
        if (sent.length === 1 && stage === "after") await firstPending;
        data = { accountId: "synthetic-import", email: "import@example.invalid", planType: "plus", status: "active" };
      } else if (p.endsWith("/usage") || p.endsWith("/trends")) data = { points: [], primary: [], secondary: [], requests: [], tokens: [] };
      await route.fulfill({ contentType: "application/json", body: JSON.stringify(data) });
    });
    await page.goto("http://127.0.0.1:4181/accounts");
    await page.addStyleTag({ content: "*,*::before,*::after{animation:none!important;transition:none!important}" });
    await expect(page.getByRole("heading", { name: "Accounts", exact: true })).toBeVisible();
    await page.getByRole("button", { name: "Add account", exact: true }).click();
    await page.getByRole("button", { name: /Import.*auth/i }).click();
    const dialog = page.getByRole("dialog");
    const input = dialog.locator('input[type="file"]');
    if (stage === "after") {
      await expect(input).toHaveAttribute("multiple", "");
      await input.setInputFiles([
        { name: "first-synthetic-auth.json", mimeType: "application/json", buffer: Buffer.from("{}") },
        { name: "second-synthetic-auth.json", mimeType: "application/json", buffer: Buffer.from("{}") },
      ]);
      await expect(dialog.getByText("second-synthetic-auth.json", { exact: true })).toBeVisible();
    }
    await expect(dialog).toHaveCSS("opacity", "1");
    await page.screenshot({ path: path.join(evidence, `${stage}-import-${width}.png`) });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    if (stage === "after") {
      await dialog.getByRole("button", { name: "Import", exact: true }).click();
      await expect(input).toBeDisabled();
      await expect(dialog.getByRole("button", { name: "Import", exact: true })).toBeDisabled();
      await page.keyboard.press("Escape");
      await dialog.getByRole("button", { name: "Close", exact: true }).click();
      await page.mouse.click(5, 5);
      await expect(dialog).toBeVisible();
      expect(sent).toHaveLength(1);
      releaseFirst!();
      await expect(dialog).not.toBeVisible();
      expect(sent).toHaveLength(2);
      expect(sent[0]).toContain('filename="first-synthetic-auth.json"');
      expect(sent[1]).toContain('filename="second-synthetic-auth.json"');
    }
  });
}
