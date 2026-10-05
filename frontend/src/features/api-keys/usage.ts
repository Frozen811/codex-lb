import type { ApiKey } from "./schemas";

export function hasApiKeyUsage(key: ApiKey): boolean {
  const usage = key.usageSummary;
  return key.lastUsedAt !== null ||
    (usage?.requestCount ?? 0) > 0 ||
    (usage?.totalTokens ?? 0) > 0 ||
    (usage?.cachedInputTokens ?? 0) > 0 ||
    (usage?.totalCostUsd ?? 0) > 0;
}
