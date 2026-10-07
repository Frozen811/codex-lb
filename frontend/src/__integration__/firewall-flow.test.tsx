import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { beforeEach, describe, expect, it } from "vitest";

import App from "@/App";
import { useAuthStore } from "@/features/auth/hooks/use-auth";
import { renderWithProviders } from "@/test/utils";
import { ADMIN_PERMISSIONS } from "@/test/mocks/factories";
import { server } from "@/test/mocks/server";

// Transform the real lazy route before the interaction timeout starts.
await import("@/features/settings/components/settings-page");

async function firewallSection() {
  // Avoid computing accessible names for every control on the large Settings
  // page. Keep explicit role/visibility checks on the matched real heading.
  const heading = await screen.findByText("Firewall", { selector: "h3" });
  expect(heading).toHaveRole("heading");
  expect(heading).toBeVisible();
  const section = heading.closest("section")!;
  expect(section).toHaveClass("scroll-mt-16");
  return within(section);
}

describe("firewall flow integration", () => {
  let entries: Array<{ ipAddress: string; createdAt: string }>;

  beforeEach(() => {
    entries = [];
    useAuthStore.setState(useAuthStore.getInitialState());

    server.use(
      http.get("/api/dashboard-auth/session", () =>
        HttpResponse.json({
          authenticated: true,
          passwordRequired: true,
          totpRequiredOnLogin: false,
          totpConfigured: true,
          role: "admin",
          permissions: ADMIN_PERMISSIONS,
        }),
      ),
      http.get("/api/firewall/ips", () =>
        HttpResponse.json({
          mode: entries.length === 0 ? "allow_all" : "allowlist_active",
          entries,
        }),
      ),
      http.post("/api/firewall/ips", async ({ request }) => {
        const payload = (await request.json()) as { ipAddress?: string };
        const ipAddress = String(payload.ipAddress || "").trim();
        const createdAt = "2026-02-18T12:00:00Z";
        entries.push({ ipAddress, createdAt });
        return HttpResponse.json({ ipAddress, createdAt });
      }),
      http.delete("/api/firewall/ips/:ipAddress", ({ params }) => {
        const ipAddress = decodeURIComponent(String(params.ipAddress));
        const index = entries.findIndex((entry) => entry.ipAddress === ipAddress);
        if (index >= 0) {
          entries.splice(index, 1);
        }
        return HttpResponse.json({ status: "deleted" });
      }),
    );
  });

  it("reveals the firewall section from the collapsed Advanced group", async () => {
    const user = userEvent.setup({ delay: null });
    window.history.pushState({}, "", "/settings");
    renderWithProviders(<App />);

    // Firewall lives in the collapsed-by-default Advanced group.
    const toggle = await screen.findByLabelText("Show advanced settings");
    expect(toggle).toHaveRole("button");
    expect(toggle).toBeVisible();
    expect(screen.queryByText("Firewall", { selector: "h3" })).not.toBeInTheDocument();
    await user.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");
    await firewallSection();
  });

  it("adds an IP and clears the input after persistence", async () => {
    const user = userEvent.setup({ delay: null });
    window.history.pushState({}, "", "/settings?advanced=1#firewall");
    renderWithProviders(<App />);
    const fw = await firewallSection();

    const input = fw.getByPlaceholderText("127.0.0.1 or 2001:db8::1");
    await user.click(input);
    await user.paste("127.0.0.1");
    await user.click(fw.getByRole("button", { name: "Add IP" }));

    expect(await fw.findByText("127.0.0.1")).toBeInTheDocument();
    expect(entries).toEqual([{ ipAddress: "127.0.0.1", createdAt: "2026-02-18T12:00:00Z" }]);
    await waitFor(() => expect(input).toHaveValue(""));
  });

  it("removes an existing IP only after confirmation", async () => {
    const user = userEvent.setup({ delay: null });
    entries.push({ ipAddress: "127.0.0.1", createdAt: "2026-02-18T12:00:00Z" });
    window.history.pushState({}, "", "/settings?advanced=1#firewall");
    renderWithProviders(<App />);

    const fw = await firewallSection();
    expect(await fw.findByText("127.0.0.1")).toBeInTheDocument();

    await user.click(fw.getByRole("button", { name: "Remove" }));

    const dialog = await screen.findByRole("alertdialog");
    expect(entries).toHaveLength(1);
    await user.click(within(dialog).getByRole("button", { name: "Remove" }));

    await waitFor(() => {
      expect(fw.queryByText("127.0.0.1")).not.toBeInTheDocument();
      expect(entries).toEqual([]);
      expect(dialog).not.toBeInTheDocument();
    });
  });

  it("redirects the legacy /firewall route to settings", async () => {
    window.history.pushState({}, "", "/firewall");
    renderWithProviders(<App />);

    expect(await screen.findByRole("heading", { name: "Settings" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/settings");
    expect(window.location.search).toBe("?advanced=1");
    expect(window.location.hash).toBe("#firewall");
    await firewallSection();
    expect(screen.getByLabelText("Hide advanced settings")).toHaveRole("button");
  });
});
