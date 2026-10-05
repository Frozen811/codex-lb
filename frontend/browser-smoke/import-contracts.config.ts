import { defineConfig } from "@playwright/test";
import { fileURLToPath } from "node:url";

export default defineConfig({
  testDir: ".",
  testMatch: "import-contracts.spec.ts",
  timeout: 30_000,
  workers: 1,
  reporter: "line",
  use: { headless: true },
  webServer: {
    cwd: fileURLToPath(new URL("..", import.meta.url)),
    command: "node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 4181",
    port: 4181,
    reuseExistingServer: false,
  },
});
