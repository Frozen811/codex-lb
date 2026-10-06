import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  testMatch: "token-import-contracts.spec.ts",
  timeout: 30_000,
  workers: 1,
  reporter: "line",
  use: { headless: true, baseURL: "http://127.0.0.1:5191" },
});
