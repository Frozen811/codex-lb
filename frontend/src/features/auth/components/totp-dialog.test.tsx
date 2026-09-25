import { fireEvent, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuthStore } from "@/features/auth/hooks/use-auth";
import { renderWithProviders } from "@/test/utils";
import { TotpDialog } from "./totp-dialog";

describe("TotpDialog", () => {
  const verifyTotp = vi.fn().mockResolvedValue(undefined);
  const logout = vi.fn().mockResolvedValue(undefined);
  const clearError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      loading: false,
      error: null,
      verifyTotp,
      logout,
      clearError,
    });
  });

  it("renders the dialog with autofill-friendly attributes", () => {
    renderWithProviders(<TotpDialog open />);

    expect(screen.getByText("Two-factor verification")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Verify" })).toBeInTheDocument();

    const input = document.querySelector('input[data-input-otp="true"]');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute("autocomplete", "one-time-code");
    expect(input).toHaveAttribute("inputmode", "numeric");
    expect(input).toHaveAttribute("name", "code");
    expect(input).toHaveAttribute("id", "totp-code");
  });

  it("does not dismiss or log out when pointerdown or focus occurs outside", () => {
    renderWithProviders(
      <div>
        <div data-testid="outside-element">Outside</div>
        <TotpDialog open />
      </div>,
    );

    const outside = screen.getByTestId("outside-element");
    fireEvent.pointerDown(outside);
    fireEvent.focus(outside);

    expect(logout).not.toHaveBeenCalled();
    expect(screen.getByText("Two-factor verification")).toBeInTheDocument();
  });

  it("submits the 6-digit verification code on complete", async () => {
    const user = userEvent.setup();
    renderWithProviders(<TotpDialog open />);

    const input = document.querySelector('input[data-input-otp="true"]') as HTMLInputElement;
    expect(input).toBeInTheDocument();

    await user.type(input, "123456");

    await waitFor(() => {
      expect(verifyTotp).toHaveBeenCalledWith("123456");
    });
  });

  it("strips non-digits from pasted or autofilled verification codes", async () => {
    renderWithProviders(<TotpDialog open />);

    const input = document.querySelector('input[data-input-otp="true"]') as HTMLInputElement;
    expect(input).toBeInTheDocument();

    fireEvent.paste(input, {
      clipboardData: {
        getData: () => "456-789",
      },
    });

    await waitFor(() => {
      expect(verifyTotp).toHaveBeenCalledWith("456789");
    });
  });
});
