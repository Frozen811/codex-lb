import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AccountAuthExportResponseSchema } from "@/features/accounts/schemas";
import { renderWithProviders } from "@/test/utils";
import { AuthExportDialog } from "./auth-export-dialog";

const accessOnly = {
  filename: "synthetic.json",
  account: { accountId: "local", chatgptAccountId: "workspace", email: "pat@example.invalid" },
  tokens: { idToken: null, accessToken: "synthetic-access", refreshToken: null, expiresAtMs: 0 },
  codexAuthJson: {
    auth_mode: "chatgpt", OPENAI_API_KEY: null, last_refresh: "2026-10-14T00:00:00Z",
    email: "pat@example.invalid", plan_type: "team", workspace_id: "workspace",
    workspace_label: "Business workspace", seat_type: "standard",
    tokens: { id_token: null, access_token: "synthetic-access", refresh_token: null, account_id: "workspace" },
  },
  opencodeAuthJson: { openai: { type: "oauth", access: "synthetic-access", refresh: "", expires: 0, accountId: "workspace" } },
};

describe("account access export contracts", () => {
  it("accepts absent optional credentials and retains identity in downloadable JSON", () => {
    const parsed = AccountAuthExportResponseSchema.parse(accessOnly);
    expect(parsed.codexAuthJson).toEqual(accessOnly.codexAuthJson);
    expect(parsed.tokens.idToken).toBeNull();
    expect(parsed.tokens.refreshToken).toBeNull();
  });

  it("renders access-only export without missing-token copy controls", async () => {
    const parsed = AccountAuthExportResponseSchema.parse(accessOnly);
    const user = userEvent.setup();
    const createObjectURL = vi.fn(() => "blob:synthetic");
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: vi.fn() });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    renderWithProviders(<AuthExportDialog open exportData={parsed} onOpenChange={vi.fn()} />);
    expect(screen.queryByRole("button", { name: "Copy ID token" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Copy refresh token" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Copy access token" })).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Download" }));
    expect(createObjectURL).toHaveBeenCalledOnce();
  });

  it("accepts older exports that omit optional credentials and metadata", () => {
    const parsed = AccountAuthExportResponseSchema.parse({
      ...accessOnly, tokens: { accessToken: "synthetic-access", expiresAtMs: 0 },
      codexAuthJson: {
        auth_mode: "chatgpt", last_refresh: accessOnly.codexAuthJson.last_refresh,
        tokens: { access_token: "synthetic-access" },
      },
    });
    expect(parsed.tokens.idToken).toBeUndefined();
    expect(parsed.codexAuthJson.tokens.refresh_token).toBeUndefined();
  });
});
