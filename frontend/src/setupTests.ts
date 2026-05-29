import { TextDecoder, TextEncoder } from "node:util";

import "@testing-library/jest-dom";

import { resetStore } from "./mocks/handlers";
import { server } from "./mocks/server";

// jsdom does not expose TextEncoder/TextDecoder as globals, but react-router
// (and other modern libraries) need them.
if (typeof globalThis.TextEncoder === "undefined") {
  globalThis.TextEncoder = TextEncoder;
}
if (typeof globalThis.TextDecoder === "undefined") {
  globalThis.TextDecoder = TextDecoder as typeof globalThis.TextDecoder;
}

// jsdom implements neither API, but Mantine relies on both.
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver;

// jsdom doesn't implement scrollIntoView; Mantine Combobox uses it when
// opening the listbox.
if (typeof Element.prototype.scrollIntoView !== "function") {
  Element.prototype.scrollIntoView = function () {};
}

beforeEach(() => {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
  });
  window.localStorage.clear();
});

// Mock the REST API with msw for the duration of the test run.
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  resetStore();
});
afterAll(() => server.close());
