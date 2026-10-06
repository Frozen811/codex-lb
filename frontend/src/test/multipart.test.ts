import { expect, it } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";

it("preserves a file body through the worker's fetch interceptors", async () => {
  const file = new File(["{}"], "auth.json", { type: "application/json" });
  const form = new FormData();
  form.append("auth_json", file);
  server.use(http.post("http://localhost/api/test-multipart", async ({ request }) => {
    const uploaded = (await request.formData()).get("auth_json") as File;
    expect(uploaded.name).toBe("auth.json");
    expect(await uploaded.text()).toBe("{}");
    return HttpResponse.json({ ok: true });
  }));
  const response = await fetch("http://localhost/api/test-multipart", { method: "POST", body: form });
  expect(response.status).toBe(200);
});
