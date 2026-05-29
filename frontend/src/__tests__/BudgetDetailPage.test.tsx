import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { Route, Routes } from "react-router";

import { seedBudget, seedCategory, seedTransaction } from "../mocks/handlers";
import { server } from "../mocks/server";
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
    const table = await getTransactionsTable();
    expect(within(table).getByText("12.50")).toBeInTheDocument();
    expect(within(table).getByText("Food")).toBeInTheDocument();
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
    const table = await getTransactionsTable();
    expect(within(table).getByText("12.50")).toBeInTheDocument();
    await userEvent.click(
      within(table).getByRole("button", { name: "Delete" }),
    );
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(
      within(dialog).getByRole("button", { name: "Delete" }),
    );
    await waitFor(() =>
      expect(within(table).queryByText("12.50")).not.toBeInTheDocument(),
    );
  });
});

async function getTransactionsTable(): Promise<HTMLElement> {
  const tables = await screen.findAllByRole("table");
  const match = tables.find((t) => within(t).queryByText(/^Date$/));
  if (!match) throw new Error("transactions table not found");
  return match;
}

// --- totals block -----------------------------------------------------------

type TotalLabel =
  | "Planned income"
  | "Actual income"
  | "Planned expense"
  | "Actual expense"
  | "Net";

function getTotal(label: TotalLabel): string {
  const stack = screen.getByText(label).parentElement!;
  return within(stack).getByText(/^-?\d/).textContent!;
}

async function findTotal(label: TotalLabel): Promise<string> {
  const labelEl = await screen.findByText(label);
  const stack = labelEl.parentElement!;
  return (await within(stack).findByText(/^-?\d/)).textContent!;
}

describe("budget detail totals", () => {
  test("shows planned and actual totals", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    const expenseCat = seedCategory({ name: "Food", kind: "expense" });
    const incomeCat = seedCategory({ name: "Salary", kind: "income" });
    seedTransaction({
      budget_id: budget.id,
      category_id: incomeCat.id,
      type: "income",
      amount: "120.00",
      date: "2026-05-05",
    });
    seedTransaction({
      budget_id: budget.id,
      category_id: expenseCat.id,
      type: "expense",
      amount: "45.50",
      date: "2026-05-10",
    });
    renderDetail(budget.id);
    expect(await findTotal("Actual income")).toBe("120.00");
    expect(getTotal("Actual expense")).toBe("45.50");
    expect(getTotal("Net")).toBe("74.50");
  });

  test("shows zero totals for a budget with no transactions", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    renderDetail(budget.id);
    expect(await findTotal("Actual income")).toBe("0.00");
    expect(getTotal("Actual expense")).toBe("0.00");
    expect(getTotal("Net")).toBe("0.00");
  });

  test("totals refresh after recording a transaction", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    seedCategory({ name: "Food", kind: "expense" });
    renderDetail(budget.id);
    expect(await findTotal("Actual expense")).toBe("0.00");

    await userEvent.click(
      screen.getByRole("button", { name: /record transaction/i }),
    );
    fireEvent.change(await screen.findByLabelText(/Amount/), {
      target: { value: "30.00" },
    });
    fireEvent.change(screen.getByLabelText(/Date/), {
      target: { value: "2026-05-10" },
    });
    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(getTotal("Actual expense")).toBe("30.00"));
    expect(getTotal("Net")).toBe("-30.00");
  });

  test("totals refresh after deleting a transaction", async () => {
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
      amount: "30.00",
      date: "2026-05-10",
    });
    renderDetail(budget.id);
    expect(await findTotal("Actual expense")).toBe("30.00");

    const transactionsTable = await getTransactionsTable();
    await userEvent.click(
      within(transactionsTable).getByRole("button", { name: "Delete" }),
    );
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(
      within(dialog).getByRole("button", { name: "Delete" }),
    );

    await waitFor(() => expect(getTotal("Actual expense")).toBe("0.00"));
    expect(getTotal("Net")).toBe("0.00");
  });

  test("surfaces a summary load error and renders no totals", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    server.use(
      http.get(
        `http://localhost:8000/budgets/${budget.id}/summary`,
        () =>
          HttpResponse.json({ detail: "Summary blew up" }, { status: 500 }),
      ),
    );
    renderDetail(budget.id);
    expect(await screen.findByText("Summary blew up")).toBeInTheDocument();
    expect(screen.queryByText("Actual income")).not.toBeInTheDocument();
    expect(screen.queryByText("Actual expense")).not.toBeInTheDocument();
    expect(screen.queryByText("Net")).not.toBeInTheDocument();
  });
});
