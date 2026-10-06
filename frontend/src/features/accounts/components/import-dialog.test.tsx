import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ImportDialog } from "@/features/accounts/components/import-dialog";

function deferred(): {
  promise: Promise<void>;
  resolve: () => void;
} {
  let resolve: (() => void) | undefined;
  const promise = new Promise<void>((resolvePromise) => {
    resolve = resolvePromise;
  });
  if (resolve === undefined) {
    throw new Error("deferred executor did not run");
  }
  return { promise, resolve };
}

describe("ImportDialog", () => {
  it("imports a pasted PAT with explicit metadata and clears the masked token", async () => {
    const user = userEvent.setup();
    const onImport = vi.fn().mockResolvedValue(undefined);
    const onOpenChange = vi.fn();
    render(
      <ImportDialog
        open
        busy={false}
        error={null}
        onOpenChange={onOpenChange}
        onImport={onImport}
      />,
    );
    await user.click(
      screen.getByRole("button", { name: "Access token" }),
    );
    expect(
      screen.getByRole("button", { name: "Import" }),
    ).toBeDisabled();
    const token = screen.getByLabelText("Access token", { exact: true });
    expect(token).toHaveAttribute("type", "password");
    await user.type(token, "synthetic-pat");
    await user.type(
      screen.getByLabelText("Email", { exact: true }),
      "pat@example.invalid",
    );
    await user.type(
      screen.getByLabelText("Upstream account ID"),
      "upstream-pat",
    );
    await user.type(
      screen.getByLabelText("Workspace ID (optional)"),
      "workspace-pat",
    );
    await user.selectOptions(
      screen.getByLabelText("Plan", { exact: true }),
      "enterprise",
    );
    await user.click(
      screen.getByRole("button", { name: "Import" }),
    );
    expect(onImport).toHaveBeenCalledTimes(1);
    const file = onImport.mock.calls[0][0] as File;
    const text = await file.text();
    expect(JSON.parse(text)).toEqual({
      tokens: { accessToken: "synthetic-pat" },
      email: "pat@example.invalid",
      accountId: "upstream-pat",
      workspaceId: "workspace-pat",
      planType: "enterprise",
    });
    expect(onOpenChange).toHaveBeenCalledWith(false);
    await user.click(
      screen.getByRole("button", { name: "Access token" }),
    );
    expect(screen.getByLabelText("Access token", { exact: true })).toHaveValue(
      "",
    );
  });

  it("guards pending token inputs and keeps failed input for retry", async () => {
    const user = userEvent.setup();
    let reject: (() => void) | undefined;
    const pending = new Promise<void>((_resolve, rejectPromise) => {
      reject = () => rejectPromise(new Error("failure"));
    });
    const onImport = vi
      .fn()
      .mockImplementationOnce(() => pending)
      .mockResolvedValue(undefined);
    const onOpenChange = vi.fn();
    render(
      <ImportDialog
        open
        busy={false}
        error={null}
        onOpenChange={onOpenChange}
        onImport={onImport}
      />,
    );
    await user.click(
      screen.getByRole("button", { name: "Access token" }),
    );
    const token = screen.getByLabelText("Access token", { exact: true });
    await user.type(token, "synthetic-pat");
    await user.type(
      screen.getByLabelText("Email", { exact: true }),
      "pat@example.invalid",
    );
    await user.type(
      screen.getByLabelText("Upstream account ID"),
      "upstream-pat",
    );
    const form = token.closest("form")!;
    fireEvent.submit(form);
    fireEvent.submit(form);
    expect(onImport).toHaveBeenCalledTimes(1);
    expect(token).toBeDisabled();
    expect(screen.getByRole("button", { name: "Auth files" })).toBeDisabled();
    await user.keyboard("{Escape}");
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
    reject!();
    await waitFor(() => expect(token).not.toBeDisabled());
    expect(token).toHaveValue("synthetic-pat");
    await user.click(
      screen.getByRole("button", { name: "Import" }),
    );
    expect(onImport).toHaveBeenCalledTimes(2);
    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false));
  });

  it("clears pasted token inputs on idle dismissal", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    render(
      <ImportDialog
        open
        busy={false}
        error={null}
        onOpenChange={onOpenChange}
        onImport={vi.fn()}
      />,
    );
    await user.click(
      screen.getByRole("button", { name: "Access token" }),
    );
    await user.type(
      screen.getByLabelText("Access token", { exact: true }),
      "synthetic-pat",
    );
    await user.click(screen.getByRole("button", { name: "Close" }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
    await user.click(
      screen.getByRole("button", { name: "Access token" }),
    );
    expect(screen.getByLabelText("Access token", { exact: true })).toHaveValue(
      "",
    );
  });

  it("does not start overlapping batches on repeated form submission", async () => {
    const user = userEvent.setup({ delay: null });
    const pending = deferred();
    const onImport = vi.fn(() => pending.promise);
    const onOpenChange = vi.fn();
    render(
      <ImportDialog
        open
        busy={false}
        error={null}
        onOpenChange={onOpenChange}
        onImport={onImport}
      />,
    );
    const input = screen.getByLabelText(/auth\.json file/i);
    await user.upload(
      input,
      new File(["{}"], "one.json", { type: "application/json" }),
    );
    const form = input.closest("form")!;
    fireEvent.submit(form);
    fireEvent.submit(form);
    expect(onImport).toHaveBeenCalledTimes(1);
    pending.resolve();
    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false));
  });

  it("allows dismissal while idle", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    render(
      <ImportDialog
        open
        busy={false}
        error={null}
        onOpenChange={onOpenChange}
        onImport={vi.fn()}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Close" }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("imports a multi-file selection sequentially and resets after success", async () => {
    const user = userEvent.setup();
    const firstImport = deferred();
    const firstFile = new File(["{}"], "first.json", {
      type: "application/json",
    });
    const secondFile = new File(["{}"], "second.json", {
      type: "application/json",
    });
    const onImport = vi
      .fn<(file: File) => Promise<void>>()
      .mockImplementationOnce(() => firstImport.promise)
      .mockResolvedValueOnce(undefined);
    const onOpenChange = vi.fn();

    render(
      <ImportDialog
        open
        busy={false}
        error={null}
        onOpenChange={onOpenChange}
        onImport={onImport}
      />,
    );

    const input = screen.getByLabelText(/auth\.json file/i);
    expect(input).toHaveAttribute("multiple");
    await user.upload(input, [firstFile, secondFile]);

    expect(screen.getByText("first.json")).toBeInTheDocument();
    expect(screen.getByText("second.json")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Import" }));

    await waitFor(() => expect(onImport).toHaveBeenCalledTimes(1));
    expect(onImport).toHaveBeenNthCalledWith(1, firstFile);
    expect(screen.getByRole("button", { name: "Import" })).toBeDisabled();

    expect(input).toBeDisabled();
    await user.keyboard("{Escape}");
    await user.click(screen.getByRole("button", { name: "Close" }));
    expect(onOpenChange).not.toHaveBeenCalled();
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    firstImport.resolve();

    await waitFor(() => expect(onImport).toHaveBeenCalledTimes(2));
    expect(onImport).toHaveBeenNthCalledWith(2, secondFile);
    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false));
    expect(screen.queryByText("first.json")).not.toBeInTheDocument();
    expect(screen.queryByText("second.json")).not.toBeInTheDocument();
  });

  it("stops on failure and retries only the failed and unattempted files", async () => {
    const user = userEvent.setup();
    const files = [
      new File(["{}"], "succeeded.json", { type: "application/json" }),
      new File(["{}"], "failed.json", { type: "application/json" }),
      new File(["{}"], "unattempted.json", { type: "application/json" }),
    ];
    let failedAttempts = 0;
    const onImport = vi.fn(async (file: File) => {
      if (file.name === "failed.json" && failedAttempts === 0) {
        failedAttempts += 1;
        throw new Error("Invalid auth file");
      }
    });
    const onOpenChange = vi.fn();

    render(
      <ImportDialog
        open
        busy={false}
        error="Invalid auth file"
        onOpenChange={onOpenChange}
        onImport={onImport}
      />,
    );

    await user.upload(screen.getByLabelText(/auth\.json file/i), files);
    await user.click(screen.getByRole("button", { name: "Import" }));

    await waitFor(() => expect(onImport).toHaveBeenCalledTimes(2));
    expect(onImport.mock.calls.map(([file]) => file.name)).toEqual([
      "succeeded.json",
      "failed.json",
    ]);
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
    expect(screen.queryByText("succeeded.json")).not.toBeInTheDocument();
    expect(screen.getByText("failed.json")).toBeInTheDocument();
    expect(screen.getByText("unattempted.json")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Import" }));

    await waitFor(() => expect(onImport).toHaveBeenCalledTimes(4));
    expect(onImport.mock.calls.map(([file]) => file.name)).toEqual([
      "succeeded.json",
      "failed.json",
      "failed.json",
      "unattempted.json",
    ]);
    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false));
  });
});
