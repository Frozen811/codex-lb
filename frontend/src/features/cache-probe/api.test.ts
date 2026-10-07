import { describe, expect, it } from "vitest";

import { getCacheProbePlan, runCacheProbe } from "@/features/cache-probe/api";

describe("cache-probe API fixtures", () => {
  it("loads a schema-valid cost preview through the real API client", async () => {
    const plan = await getCacheProbePlan();
    expect(plan.totalCalls).toBe(plan.seedRepetitions + plan.availableOtherAccounts.length);
    expect(plan.estimatedTotalInputTokens).toBe(plan.totalCalls * plan.estimatedInputTokensPerCall);
    expect(plan.pressure.underPressure).toBe(false);
  });

  it("returns deterministic, consistent accounting for a confirmed run", async () => {
    const result = await runCacheProbe({ confirm: true, seedRepetitions: 2, otherAccountCount: 1 });
    expect(result.calls.map(({ sequence, role }) => ({ sequence, role }))).toEqual([
      { sequence: 1, role: "seed" },
      { sequence: 2, role: "seed" },
      { sequence: 3, role: "other" },
    ]);
    expect(result.seedCallCount).toBe(2);
    expect(result.otherCallCount).toBe(1);
    expect(result.crossAccountHit).toBe(false);
    expect(result.verdict).toBe("no_cross_account_hit");
  });

  it("rejects an unconfirmed request at the mock transport boundary", async () => {
    const response = await fetch("/api/diagnostics/cache-isolation-probe/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirm: false, seedRepetitions: 2, otherAccountCount: 1 }),
    });
    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({ error: { code: "invalid_probe_request" } });
  });
});
