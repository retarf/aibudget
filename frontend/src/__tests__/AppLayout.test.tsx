import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router";

import { App } from "../App";
import { theme } from "../theme";

function renderApp(path = "/"): ReactElement | void {
  render(
    <MantineProvider theme={theme}>
      <MemoryRouter initialEntries={[path]}>
        <App />
      </MemoryRouter>
    </MantineProvider>,
  );
}

describe("app shell", () => {
  test("renders the shell with a left navigation menu", () => {
    renderApp();
    expect(screen.getByRole("link", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Budgets" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Categories" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Reports" })).toBeInTheDocument();
  });

  test("navigating to a section shows that section", async () => {
    renderApp();
    await userEvent.click(screen.getByRole("link", { name: "Budgets" }));
    expect(
      screen.getByRole("heading", { name: "Budgets", level: 2 }),
    ).toBeInTheDocument();
  });

  test("the active section's menu item is marked active", async () => {
    renderApp();
    await userEvent.click(screen.getByRole("link", { name: "Budgets" }));
    expect(screen.getByRole("link", { name: "Budgets" })).toHaveAttribute(
      "data-active",
    );
  });

  test("an unknown route shows the not-found view inside the shell", () => {
    renderApp("/does-not-exist");
    expect(
      screen.getByRole("heading", { name: "Page not found", level: 2 }),
    ).toBeInTheDocument();
    // The shell is still present.
    expect(screen.getByRole("link", { name: "Dashboard" })).toBeInTheDocument();
  });
});
