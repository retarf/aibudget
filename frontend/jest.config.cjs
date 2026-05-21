/** @type {import('jest').Config} */
module.exports = {
  // jest-fixed-jsdom keeps Node's fetch/Response/Request globals so msw works.
  testEnvironment: "jest-fixed-jsdom",
  setupFilesAfterEnv: ["<rootDir>/src/setupTests.ts"],
  moduleNameMapper: {
    // Mantine style imports are not relevant to component tests.
    "\\.(css|scss)$": "identity-obj-proxy",
  },
  // babel-jest transforms our TS/TSX and msw's ESM-only dependencies. The
  // babel config is inline (configFile/babelrc false) so Vite is unaffected.
  transform: {
    "^.+\\.(mjs|cjs|jsx?|tsx?)$": [
      "babel-jest",
      {
        configFile: false,
        babelrc: false,
        presets: [
          ["@babel/preset-env", { targets: { node: "current" } }],
          ["@babel/preset-react", { runtime: "automatic" }],
          "@babel/preset-typescript",
        ],
      },
    ],
  },
  // node_modules is not transformed, except msw and its ESM-only dependencies.
  transformIgnorePatterns: [
    "/node_modules/(?!(msw|@mswjs|@bundled-es-modules|@open-draft|rettime" +
      "|until-async|strict-event-emitter|headers-polyfill|outvariant" +
      "|is-node-process|path-to-regexp)/)",
  ],
  // Vite's `define` global, supplied here for tests.
  globals: {
    __API_URL__: "http://localhost:8000",
  },
};
