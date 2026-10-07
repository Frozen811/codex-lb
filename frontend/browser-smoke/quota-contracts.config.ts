import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "@playwright/test";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export default defineConfig({
  testDir: ".",
  testMatch: "quota-contracts.spec.ts",
  timeout: 30_000,
  workers: 1,
  reporter: "line",
  use: { headless: true },
  webServer: {
    command: "node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 4183",
    cwd: frontendRoot,
    port: 4183,
    reuseExistingServer: false,
  },
});
