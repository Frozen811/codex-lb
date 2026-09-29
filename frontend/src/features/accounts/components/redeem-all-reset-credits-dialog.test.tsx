import { HttpResponse, http } from "msw";
import type { ReactElement } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { RedeemAllResetCreditsDialog } from "@/features/accounts/components/redeem-all-reset-credits-dialog";
import { server } from "@/test/mocks/server";

const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: {
    success: toastSuccess,
    error: toastError,
  },
}));

const REDEEM_ALL_URL = "/api/accounts/rate-limit-reset-credits/redeem-all";

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
}

function renderWithClient(ui: ReactElement) {
  const queryClient = createTestQueryClient();
  const renderResult = render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
  return { queryClient, ...renderResult };
}

describe("RedeemAllResetCreditsDialog", () => {
  it("renders eligible accounts and total credits", () => {
    const accounts = [
      {
        accountId: "acc_1",
        displayName: "Account 1",
        email: "acc1@example.com",
        alias: "Work Account",
        availableResetCredits: 2,
      },
      {
        accountId: "acc_2",
        displayName: "Account 2",
        email: "acc2@example.com",
        availableResetCredits: 1,
      },
    ];

    renderWithClient(
      <RedeemAllResetCreditsDialog
        open={true}
        onOpenChange={vi.fn()}
        eligibleAccounts={accounts}
      />,
    );

    expect(screen.getByText("Total credits to redeem:")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("Work Account")).toBeInTheDocument();
    expect(screen.getByText("Account 2")).toBeInTheDocument();
  });

  it("triggers bulk redeem on confirm", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();

    let endpointCalled = false;
    server.use(
      http.post(REDEEM_ALL_URL, () => {
        endpointCalled = true;
        return HttpResponse.json({
          totalAccountsAttempted: 1,
          totalAccountsSucceeded: 1,
          totalCreditsRedeemed: 2,
          results: [
            {
              accountId: "acc_1",
              success: true,
              creditsRedeemed: 2,
            },
          ],
        });
      }),
    );

    const accounts = [
      {
        accountId: "acc_1",
        displayName: "Account 1",
        email: "acc1@example.com",
        availableResetCredits: 2,
      },
    ];

    renderWithClient(
      <RedeemAllResetCreditsDialog
        open={true}
        onOpenChange={onOpenChange}
        eligibleAccounts={accounts}
      />,
    );

    const confirmButton = screen.getByRole("button", { name: /Redeem all credits/i });
    await user.click(confirmButton);

    expect(endpointCalled).toBe(true);
  });
});
