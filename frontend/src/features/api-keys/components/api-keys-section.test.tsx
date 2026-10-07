import { Suspense } from "react";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { expect, it, vi } from "vitest";
import { createApiKey } from "@/test/mocks/factories";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/utils";
import { ApiKeysSection } from "./api-keys-section";

it("reports partial reset errors and retains failed keys for retry", async () => {
  const keys = [createApiKey({ id: "ok", name: "Succeeded key" }), createApiKey({ id: "bad", name: "Failed key" })];
  server.use(
    http.get("/api/api-keys/", () => HttpResponse.json(keys)),
    http.patch("/api/api-keys/:id", ({ params }) => params.id === "bad"
      ? HttpResponse.json({ error: { code: "conflict", message: "Try again" } }, { status: 409 })
      : HttpResponse.json(keys[0])),
  );
  renderWithProviders(<Suspense><ApiKeysSection apiKeyAuthEnabled={false} hideUpstreamQuotaFromApiKeys={false}
    onApiKeyAuthEnabledChange={vi.fn()} onHideUpstreamQuotaFromApiKeysChange={vi.fn()} /></Suspense>);
  const user = userEvent.setup();
  await user.click(await screen.findByRole("checkbox", { name: "Succeeded key" }));
  await user.click(screen.getByRole("checkbox", { name: "Failed key" }));
  await user.click(screen.getByRole("button", { name: "Reset usage (2)" }));
  const dialog = screen.getByRole("alertdialog");
  expect(dialog).toHaveTextContent("Succeeded key");
  expect(dialog).toHaveTextContent("Failed key");
  await user.click(within(dialog).getByRole("button", { name: "Reset usage" }));
  await waitFor(() => expect(screen.getByRole("checkbox", { name: "Failed key" })).toBeChecked());
  await waitFor(() => expect(screen.getByText("Failed key: Try again")).toBeInTheDocument());
  expect(screen.getByRole("checkbox", { name: "Succeeded key" })).not.toBeChecked();
});
