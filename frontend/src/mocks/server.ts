import { setupServer } from "msw/node";

import { handlers } from "./handlers";

// msw server for tests. Activate it from setupTests.ts once feature pages
// start calling the REST API.
export const server = setupServer(...handlers);
