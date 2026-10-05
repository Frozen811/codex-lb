import { describe, expect, it } from "vitest";
import { hasApiKeyUsage } from "./usage";
import { createApiKey } from "@/test/mocks/factories";

describe("recorded API key usage", () => {
  it.each([
    ["requestCount", 1], ["totalTokens", 1], ["cachedInputTokens", 1], ["totalCostUsd", 0.01],
  ])("recognizes positive %s without last-used metadata", (field, value) => {
    const usage = { requestCount: 0, totalTokens: 0, cachedInputTokens: 0, totalCostUsd: 0, [field]: value };
    expect(hasApiKeyUsage(createApiKey({ lastUsedAt: null, usageSummary: usage }))).toBe(true);
  });
  it("keeps a recorded last use when summaries are missing", () => {
    expect(hasApiKeyUsage(createApiKey({ lastUsedAt: "2026-10-05T00:00:00Z", usageSummary: null }))).toBe(true);
  });
  it("treats missing summaries and known zero as unused", () => {
    for (const usageSummary of [null, { requestCount: 0, totalTokens: 0, cachedInputTokens: 0, totalCostUsd: 0 }]) {
      expect(hasApiKeyUsage(createApiKey({ lastUsedAt: null, usageSummary }))).toBe(false);
    }
  });
});
