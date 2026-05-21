import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { seedBudget } from "../mocks/handlers";
import { BudgetsPage } from "../pages/BudgetsPage";
import { renderWithProviders } from "../test-utils";

describe("budget pages", () => {
  test("lists existing budgets", async () => {
    seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    renderWithProviders(<BudgetsPage />);
    expect(await screen.findByText("May")).toBeInTheDocument();
  });

  test("shows an empty state when there are no budgets", async () => {
    renderWithProviders(<BudgetsPage />);
    expect(await screen.findByText(/no budgets yet/i)).toBeInTheDocument();
  });

  test("creates a budget", async () => {
    renderWithProviders(<BudgetsPage />);
    await userEvent.click(screen.getByRole("button", { name: /new budget/i }));
    const nameInput = await screen.findByLabelText(/Name/);
    await userEvent.type(nameInput, "June");
    fireEvent.change(screen.getByLabelText(/Start date/), {
      target: { value: "2026-06-01" },
    });
    fireEvent.change(screen.getByLabelText(/End date/), {
      target: { value: "2026-06-30" },
    });
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("June")).toBeInTheDocument();
  });

  test("surfaces the API error for an invalid period", async () => {
    renderWithProviders(<BudgetsPage />);
    await userEvent.click(screen.getByRole("button", { name: /new budget/i }));
    const nameInput = await screen.findByLabelText(/Name/);
    await userEvent.type(nameInput, "Bad");
    fireEvent.change(screen.getByLabelText(/Start date/), {
      target: { value: "2026-06-30" },
    });
    fireEvent.change(screen.getByLabelText(/End date/), {
      target: { value: "2026-06-01" },
    });
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(
      await screen.findByText(/end_date must be after start_date/i),
    ).toBeInTheDocument();
  });

  test("deletes a budget", async () => {
    seedBudget({
      name: "Old",
      start_date: "2026-01-01",
      end_date: "2026-01-31",
    });
    renderWithProviders(<BudgetsPage />);
    await screen.findByText("Old");
    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(
      within(dialog).getByRole("button", { name: "Delete" }),
    );
    await waitFor(() =>
      expect(screen.queryByText("Old")).not.toBeInTheDocument(),
    );
  });
});
