import {
  MantineProvider,
  localStorageColorSchemeManager,
} from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ThemeToggle } from "../components/ThemeToggle";
import { theme } from "../theme";

function colorScheme(): string | null {
  return document.documentElement.getAttribute("data-mantine-color-scheme");
}

describe("theme switching", () => {
  test("renders a theme toggle control", () => {
    render(
      <MantineProvider theme={theme} defaultColorScheme="light">
        <ThemeToggle />
      </MantineProvider>,
    );
    expect(
      screen.getByRole("button", { name: /toggle color scheme/i }),
    ).toBeInTheDocument();
  });

  test("toggling switches the color scheme", async () => {
    render(
      <MantineProvider theme={theme} defaultColorScheme="light">
        <ThemeToggle />
      </MantineProvider>,
    );
    expect(colorScheme()).toBe("light");
    await userEvent.click(
      screen.getByRole("button", { name: /toggle color scheme/i }),
    );
    expect(colorScheme()).toBe("dark");
  });

  test("the chosen theme is persisted to localStorage", async () => {
    render(
      <MantineProvider
        theme={theme}
        defaultColorScheme="light"
        colorSchemeManager={localStorageColorSchemeManager({
          key: "mantine-color-scheme-value",
        })}
      >
        <ThemeToggle />
      </MantineProvider>,
    );
    await userEvent.click(
      screen.getByRole("button", { name: /toggle color scheme/i }),
    );
    expect(localStorage.getItem("mantine-color-scheme-value")).toBe("dark");
  });

  test("defaults to the OS color-scheme preference", () => {
    window.matchMedia = ((query: string) => ({
      matches: query.includes("dark"),
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    })) as unknown as typeof window.matchMedia;

    render(
      <MantineProvider theme={theme} defaultColorScheme="auto">
        <ThemeToggle />
      </MantineProvider>,
    );
    expect(colorScheme()).toBe("dark");
  });
});
