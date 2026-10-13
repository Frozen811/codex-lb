import { chromium } from "../../../frontend/node_modules/playwright";
import { authSession, overview, settings, models } from "../../../frontend/screenshots/fixtures";
import { createAccountSummary } from "../../../frontend/src/test/mocks/factories";
import fs from "node:fs/promises";
import path from "node:path";

const output = path.resolve("../openspec/changes/complete-account-window-reserves/screenshots");
await fs.mkdir(output, { recursive: true });
const account = createAccountSummary({
  email: "reserve@example.invalid", displayName: "Reserve example", planType: "pro",
  usageLimitEnabled: true, usageLimitPercent: 80, usageLimit5HPercent: 60, usageLimitWeeklyPercent: 80,
  effectiveLimitPrimary: 60, effectiveLimitSecondary: 80, usageLimitState: "available",
  usage: { primaryRemainingPercent: 82, secondaryRemainingPercent: 70, monthlyRemainingPercent: null },
});
const browser = await chromium.launch({ headless: true });
try {
  for (const [version, port] of [["before", 4176], ["after", 4175]] as const) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1050 }, reducedMotion: "reduce" });
    await page.addInitScript(() => {
      localStorage.setItem("codex-lb-theme", "light");
    });
    await page.route("**/api/**", async route => {
      const p = new URL(route.request().url()).pathname;
      const data = p === "/api/dashboard-auth/session" ? authSession
        : p === "/api/accounts" ? { accounts: [account] }
          : p === "/api/settings" ? settings
            : p === "/api/dashboard/overview" ? overview
              : p === "/api/models" ? { models }
                : null;
      if (data === null) return route.abort();
      await route.fulfill({ contentType: "application/json", body: JSON.stringify(data) });
    });
    await page.route("**/health", route => route.fulfill({ contentType: "application/json", body: '{"status":"ok"}' }));
    await page.goto(`http://127.0.0.1:${port}/accounts`, { waitUntil: "networkidle" });
    await page.getByText("Reserve example", { exact: true }).first().waitFor();
    await page.evaluate(() => { const footer = document.querySelector("footer"); if (footer) footer.style.position = "relative"; });
    await page.screenshot({ path: path.join(output, `${version}-accounts.png`), fullPage: true });
    if (version === "after") {
      const editor = page.getByRole("heading", { name: "Keep quota for yourself" }).locator("xpath=ancestor::section[1]");
      await editor.screenshot({ path: path.join(output, "after-reserve-editor.png") });
    }
    await page.close();
  }
} finally {
  await browser.close();
}
console.log(output);
