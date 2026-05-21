import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router";

import { seedBudget, seedCategory, seedTransaction } from "../mocks/handlers";
import { BudgetDetailPage } from "../pages/BudgetDetailPage";
import { renderWithProviders } from "../test-utils";

function renderDetail(budgetId: number) {
  return renderWithProviders(
    <Routes>
      <Route path="/budgets/:budgetId" element={<BudgetDetailPage />} />
    </Routes>,
    { route: `/budgets/${budgetId}` },
  );
}

describe("transaction pages", () => {
  test("lists a budget's transactions", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    const category = seedCategory({ name: "Food", kind: "expense" });
    seedTransaction({
      budget_id: budget.id,
      category_id: category.id,
      type: "expense",
      amount: "12.50",
      date: "2026-05-10",
    });
    renderDetail(budget.id);
    expect(await screen.findByText("12.50")).toBeInTheDocument();
    expect(screen.getByText("Food")).toBeInTheDocument();
  });

  test("shows an empty state when a budget has no transactions", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    renderDetail(budget.id);
    expect(await screen.findByText(/no transactions yet/i)).toBeInTheDocument();
  });

  test("deletes a transaction", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    const category = seedCategory({ name: "Food", kind: "expense" });
    seedTransaction({
      budget_id: budget.id,
      category_id: category.id,
      type: "expense",
      amount: "12.50",
      date: "2026-05-10",
    });
    renderDetail(budget.id);
    await screen.findByText("12.50");
    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(
      within(dialog).getByRole("button", { name: "Delete" }),
    );
    await waitFor(() =>
      expect(screen.queryByText("12.50")).not.toBeInTheDocument(),
    );
  });
});
