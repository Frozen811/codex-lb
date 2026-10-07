import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  testMatch: "key-quota.spec.ts",
  workers: 1,
  timeout: 30_000,
  reporter: "line",
  use: { headless: true, baseURL: process.env.KEY_QUOTA_BASE_URL ?? "http://127.0.0.1:4173" },
});
