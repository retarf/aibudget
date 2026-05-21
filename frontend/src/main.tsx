import { MantineProvider, localStorageColorSchemeManager } from "@mantine/core";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";

import "@mantine/core/styles.css";

import { App } from "./App";
import { theme } from "./theme";

// Persists the user's chosen color scheme; the key matches the inline script
// in index.html that applies it before first paint.
const colorSchemeManager = localStorageColorSchemeManager({
  key: "mantine-color-scheme-value",
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <MantineProvider
      theme={theme}
      defaultColorScheme="auto"
      colorSchemeManager={colorSchemeManager}
    >
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </MantineProvider>
  </StrictMode>,
);
