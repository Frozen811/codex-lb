import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "@playwright/test";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export default defineConfig({
  testDir: ".", testMatch: "account-access.spec.ts", timeout: 30_000, workers: 1, reporter: "line",
  use: { baseURL: "http://127.0.0.1:4187", headless: true, locale: "en-US" },
  webServer: {
    command: "node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 4187 --strictPort",
    cwd: frontendRoot, port: 4187, reuseExistingServer: false,
  },
});
