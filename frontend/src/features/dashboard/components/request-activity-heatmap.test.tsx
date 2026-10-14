import { fireEvent, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";

import { activityCalendar } from "@/features/dashboard/activity-calendar";
import { RequestActivityHeatmap } from "@/features/dashboard/components/request-activity-heatmap";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/utils";
import { TooltipProvider } from "@/components/ui/tooltip";

const activity = { startDate: "2026-05-01", endDate: "2026-10-14", days: [{ date: "2026-10-14", requests: 7 }] };

describe("request heatmap", () => {
  it("aligns UTC leap-day cells and zero days", () => {
    const cells = activityCalendar({ startDate: "2024-02-28", endDate: "2024-03-01", days: [{ date: "2024-02-29", requests: 2 }] });
    expect(cells.slice(0, 3)).toEqual([null, null, null]);
    expect(cells.slice(3)).toEqual([
      { date: "2024-02-28", requests: 0, level: 0 },
      { date: "2024-02-29", requests: 2, level: 4 },
      { date: "2024-03-01", requests: 0, level: 0 },
    ]);
  });
  it("shows reported and zero days with accessible tooltips", async () => {
    server.use(http.get("/api/dashboard/request-activity", () => HttpResponse.json(activity)));
    renderWithProviders(<TooltipProvider><RequestActivityHeatmap /></TooltipProvider>);
    expect(await screen.findByRole("button", { name: "2026-10-14 · 7 requests" })).toBeVisible();
    expect(screen.getByRole("button", { name: "2026-05-01 · 0 requests" })).toBeVisible();
    expect(screen.getByText("Less")).toBeVisible();
  });
  it("retries an activity failure", async () => {
    let calls = 0;
    server.use(http.get("/api/dashboard/request-activity", () => ++calls === 1 ? new HttpResponse(null, { status: 503 }) : HttpResponse.json(activity)));
    renderWithProviders(<TooltipProvider><RequestActivityHeatmap /></TooltipProvider>);
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not load request activity.");
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findByRole("button", { name: "2026-10-14 · 7 requests" })).toBeVisible();
  });
});
