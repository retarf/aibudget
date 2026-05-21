/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/src/setupTests.ts"],
  moduleNameMapper: {
    // Mantine style imports are not relevant to component tests.
    "\\.(css|scss)$": "identity-obj-proxy",
  },
};
