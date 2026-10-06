import "@/test/setup-local-storage";
import "@testing-library/jest-dom/vitest";
import { cleanup, configure } from "@testing-library/react";
import { afterAll, afterEach, beforeAll, vi } from "vitest";
import { Blob, File } from "node:buffer";

import "@/i18n";
import { resetMockState } from "@/test/mocks/handlers";
import { server, startMockServer } from "@/test/mocks/server";

// Keep multipart/file constructors in the same realm as the Node fetch stack.
// jsdom FormData passed to a native Request is otherwise encoded as text/plain.
// Install them before MSW starts; each isolated worker owns its interceptors.
Object.assign(globalThis, { Blob, File });
Object.assign(window, { Blob, File });
// Undici captures Blob/File when its WebIDL module loads. Import only after
// assigning them, so FormData.append recognizes files instead of stringifying.
const { FormData, Headers, Request, Response } = await import("undici");
Object.assign(globalThis, { FormData, Headers, Request, Response });
Object.assign(window, { FormData, Headers, Request, Response });

if (typeof window !== "undefined" && typeof window.matchMedia !== "function") {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

if (typeof document !== "undefined" && typeof document.elementFromPoint !== "function") {
  document.elementFromPoint = () => null;
}

if (typeof Element !== "undefined") {
  const proto = Element.prototype as unknown as Record<string, unknown>;
  if (typeof proto.hasPointerCapture !== "function") {
    Object.defineProperty(Element.prototype, "hasPointerCapture", {
      configurable: true,
      value: () => false,
    });
  }
  if (typeof proto.setPointerCapture !== "function") {
    Object.defineProperty(Element.prototype, "setPointerCapture", {
      configurable: true,
      value: () => {},
    });
  }
  if (typeof proto.releasePointerCapture !== "function") {
    Object.defineProperty(Element.prototype, "releasePointerCapture", {
      configurable: true,
      value: () => {},
    });
  }
  if (typeof proto.scrollIntoView !== "function") {
    Object.defineProperty(Element.prototype, "scrollIntoView", {
      configurable: true,
      value: () => {},
    });
  }
}

if (typeof globalThis.ResizeObserver === "undefined") {
  class ResizeObserverMock {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
  globalThis.ResizeObserver = ResizeObserverMock;
}

beforeAll(() => {
  configure({ asyncUtilTimeout: 10_000 });
  startMockServer();
});

afterEach(() => {
  // Unmount while this test's handlers and spies are still installed.
  cleanup();
  vi.useRealTimers();
  vi.clearAllMocks();
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  if (typeof window !== "undefined") {
    window.history.replaceState({}, "", "/");
    try {
      window.localStorage.clear();
      window.sessionStorage.clear();
    } catch {
      /* ignore */
    }
  }
  resetMockState();
  server.resetHandlers();
});

afterAll(() => {
  server.close();
});
