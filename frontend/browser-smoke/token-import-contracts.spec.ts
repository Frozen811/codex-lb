import path from "node:path";
import { expect, test } from "@playwright/test";
import {
  accounts,
  authSession,
  settings,
  upstreamProxyAdmin,
} from "../screenshots/fixtures";

const stage = process.env.TOKEN_IMPORT_STAGE ?? "after";
const evidence = process.env.TOKEN_IMPORT_EVIDENCE_DIR!;

for (const width of [1440, 390]) {
  test(`token import at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.addInitScript(() =>
      localStorage.setItem("codex-lb-language", "en"),
    );
    const sent: string[] = [];
    let release: (() => void) | undefined;
    const pending = new Promise<void>((resolve) => {
      release = resolve;
    });
    await page.route("**/health/ready", (route) =>
      route.fulfill({ json: { status: "ok" } }),
    );
    await page.route("**/api/**", async (route) => {
      const endpoint = new URL(route.request().url()).pathname;
      let data: unknown = {};
      if (endpoint === "/api/dashboard-auth/session") data = authSession;
      else if (endpoint === "/api/accounts") data = { accounts };
      else if (endpoint === "/api/settings") data = settings;
      else if (endpoint === "/api/settings/upstream-proxy")
        data = upstreamProxyAdmin;
      else if (endpoint === "/api/accounts/import") {
        sent.push(route.request().postData() ?? "");
        if (sent.length === 1) {
          await pending;
          await route.fulfill({
            status: 400,
            json: {
              error: {
                code: "invalid_auth_json",
                message: "Synthetic import failure",
              },
            },
          });
          return;
        }
        data = {
          accountId: "synthetic-pat",
          email: "pat@example.invalid",
          planType: "enterprise",
          status: "active",
        };
      } else if (endpoint.endsWith("/usage") || endpoint.endsWith("/trends")) {
        data = {
          points: [],
          primary: [],
          secondary: [],
          requests: [],
          tokens: [],
        };
      }
      await route.fulfill({ json: data });
    });
    await page.goto("/accounts");
    await page.addStyleTag({
      content:
        "*,*::before,*::after{animation:none!important;transition:none!important}",
    });
    await page
      .getByRole("button", { name: "Add account", exact: true })
      .click();
    await page.getByRole("button", { name: /Import.*auth/i }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    if (stage === "after") {
      await dialog
        .getByRole("button", { name: "Access token", exact: true })
        .click();
      await dialog
        .getByLabel("Access token", { exact: true })
        .fill("synthetic-pat-secret");
      await dialog
        .getByLabel("Email", { exact: true })
        .fill("pat@example.invalid");
      await dialog
        .getByLabel("Upstream account ID", { exact: true })
        .fill("synthetic-upstream-id");
      await dialog
        .getByLabel("Plan", { exact: true })
        .selectOption("enterprise");
      await dialog
        .getByLabel("Workspace ID (optional)")
        .fill("synthetic-workspace");
      await expect(
        dialog.getByLabel("Access token", { exact: true }),
      ).toHaveAttribute("type", "password");
    }
    await expect(dialog).toHaveCSS("opacity", "1");
    await page.screenshot({
      path: path.join(evidence, `${stage}-token-import-${width}.png`),
    });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
    if (stage === "before") return;

    await dialog.getByRole("button", { name: "Import", exact: true }).click();
    await expect(
      dialog.getByLabel("Access token", { exact: true }),
    ).toBeDisabled();
    await expect(
      dialog.getByRole("button", { name: "Auth files" }),
    ).toBeDisabled();
    await page.keyboard.press("Escape");
    await dialog.getByRole("button", { name: "Close", exact: true }).click();
    await expect(dialog).toBeVisible();
    expect(sent).toHaveLength(1);
    release!();
    await expect(dialog.getByText("Synthetic import failure")).toBeVisible();
    await expect(
      dialog.getByLabel("Access token", { exact: true }),
    ).toHaveValue("synthetic-pat-secret");
    await dialog.getByRole("button", { name: "Import", exact: true }).click();
    await expect(dialog).not.toBeVisible();
    expect(sent).toHaveLength(2);
    for (const body of sent) {
      expect(body).toContain('"accessToken":"synthetic-pat-secret"');
      expect(body).toContain('"accountId":"synthetic-upstream-id"');
      expect(body).toContain('"workspaceId":"synthetic-workspace"');
      expect(body).toContain('"planType":"enterprise"');
      expect(body).not.toContain("refreshToken");
    }
    expect(
      await page.evaluate(
        () => JSON.stringify(localStorage) + JSON.stringify(sessionStorage),
      ),
    ).not.toContain("synthetic-pat-secret");
    await page
      .getByRole("button", { name: "Add account", exact: true })
      .click();
    await page.getByRole("button", { name: /Import.*auth/i }).click();
    await dialog
      .getByRole("button", { name: "Access token", exact: true })
      .click();
    await expect(
      dialog.getByLabel("Access token", { exact: true }),
    ).toHaveValue("");
  });
}
