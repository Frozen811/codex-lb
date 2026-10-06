import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";

import App from "@/App";
import { renderWithProviders } from "@/test/utils";
import { server } from "@/test/mocks/server";

describe("accounts flow integration", () => {
  it("imports through the per-file API and retries only the rejected suffix", async () => {
    const user = userEvent.setup({ delay: null });
    const observed: string[] = [];
    let fail = true;
    server.use(http.post("/api/accounts/import", async ({ request }) => {
      expect(request.headers.get("content-type")).toContain("multipart/form-data");
      const uploaded = (await request.formData()).get("auth_json");
      expect(uploaded).toMatchObject({ name: expect.any(String), type: "application/json" });
      const name = (uploaded as File).name;
      observed.push(name);
      if (name === "second.json" && fail) {
        fail = false;
        return HttpResponse.json({ error: { code: "invalid_auth", message: "Invalid auth file" } }, { status: 400 });
      }
      return HttpResponse.json({ accountId: name, email: "synthetic@example.invalid", planType: "plus", status: "active" });
    }));
    window.history.pushState({}, "", "/accounts");
    renderWithProviders(<App />);
    await user.click(await screen.findByRole("button", { name: "Add account" }));
    await user.click(screen.getByRole("button", { name: /Import.*auth/i }));
    // Radix registers its modal layer on the next frame. Its input is present
    // before the layer accepts pointer events, especially under CPU contention.
    const dialog = await screen.findByRole("dialog");
    await waitFor(() => expect(dialog).toHaveStyle({ pointerEvents: "auto" }));
    await user.upload(await screen.findByLabelText(/auth\.json file/i), ["first.json", "second.json", "third.json"].map(name => new File(["{}"], name, { type: "application/json" })));
    await user.click(screen.getByRole("button", { name: "Import" }));
    await waitFor(() => expect(observed).toEqual(["first.json", "second.json"]));
    expect((await screen.findAllByText("Invalid auth file")).length).toBeGreaterThan(0);
    expect(observed).toEqual(["first.json", "second.json"]);
    expect(screen.queryByText("first.json")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Import" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(observed).toEqual(["first.json", "second.json", "second.json", "third.json"]);
  });

  it("supports account selection and pause/resume actions", async () => {
    const user = userEvent.setup({ delay: null });

    window.history.pushState({}, "", "/accounts");
    renderWithProviders(<App />);

    expect(await screen.findByRole("heading", { name: "Accounts" })).toBeInTheDocument();
    expect((await screen.findAllByText("primary@example.com")).length).toBeGreaterThan(0);
    expect(screen.getByText("secondary@example.com")).toBeInTheDocument();

    await user.click(screen.getByText("secondary@example.com"));
    expect(await screen.findByText("Token Status")).toBeInTheDocument();

    const resumeButton = screen.queryByRole("button", { name: "Resume" });
    if (resumeButton) {
      await user.click(resumeButton);
      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Pause" })).toBeInTheDocument();
      });
    } else {
      await user.click(screen.getByRole("button", { name: "Pause" }));
      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Resume" })).toBeInTheDocument();
      });
    }
  });

  it("lets operators set, search, and clear an account alias", async () => {
    const user = userEvent.setup({ delay: null });

    window.history.pushState({}, "", "/accounts");
    renderWithProviders(<App />);

    expect(await screen.findByRole("heading", { name: "Accounts" })).toBeInTheDocument();
    await user.click(await screen.findByRole("button", { name: "Edit alias" }));
    const aliasInput = await screen.findByLabelText("Account alias");
    await user.clear(aliasInput);
    await user.type(aliasInput, "Personal Plus");
    await user.click(screen.getByRole("button", { name: "Save alias" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Personal Plus" })).toBeInTheDocument();
    });

    await user.type(screen.getByPlaceholderText("Search accounts..."), "personal");
    expect(screen.getAllByText("Personal Plus").length).toBeGreaterThan(0);
    expect(screen.queryByText("secondary@example.com")).not.toBeInTheDocument();

    await user.click(await screen.findByRole("button", { name: "Edit alias" }));
    const aliasInputToClear = await screen.findByLabelText("Account alias");
    await user.clear(aliasInputToClear);
    await user.click(screen.getByRole("button", { name: "Save alias" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "primary@example.com" })).toBeInTheDocument();
    });
  });
});
