import "@testing-library/jest-dom";

// jsdom implements neither API, but Mantine relies on both.
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver;

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

// msw is scaffolded in src/mocks/. Once feature pages call the REST API,
// activate it here:
//   import { server } from "./mocks/server";
//   beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
//   afterEach(() => server.resetHandlers());
//   afterAll(() => server.close());
