import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";

import {
  seedBudget,
  seedCategory,
  seedTransaction,
} from "../mocks/handlers";
import { server } from "../mocks/server";
import { BudgetsPage } from "../pages/BudgetsPage";
import { renderWithProviders } from "../test-utils";

function getRow(name: string): HTMLElement {
  return screen.getByRole("row", { name: new RegExp(name) });
}

async function findRow(name: string): Promise<HTMLElement> {
  return screen.findByRole("row", { name: new RegExp(name) });
}

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

describe("budget list totals", () => {
  test("shows per-row income, expense and net for each budget", async () => {
    const may = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    const june = seedBudget({
      name: "June",
      start_date: "2026-06-01",
      end_date: "2026-06-30",
    });
    const expenseCat = seedCategory({ name: "Food", kind: "expense" });
    const incomeCat = seedCategory({ name: "Salary", kind: "income" });
    seedTransaction({
      budget_id: may.id,
      category_id: incomeCat.id,
      type: "income",
      amount: "120.00",
      date: "2026-05-05",
    });
    seedTransaction({
      budget_id: may.id,
      category_id: expenseCat.id,
      type: "expense",
      amount: "45.50",
      date: "2026-05-10",
    });
    seedTransaction({
      budget_id: june.id,
      category_id: expenseCat.id,
      type: "expense",
      amount: "10.00",
      date: "2026-06-05",
    });

    renderWithProviders(<BudgetsPage />);

    await waitFor(() => {
      const mayRow = getRow("May");
      expect(within(mayRow).getByText("120.00")).toBeInTheDocument();
      expect(within(mayRow).getByText("45.50")).toBeInTheDocument();
      expect(within(mayRow).getByText("74.50")).toBeInTheDocument();
    });

    const juneRow = getRow("June");
    expect(within(juneRow).getByText("0.00")).toBeInTheDocument();
    expect(within(juneRow).getByText("10.00")).toBeInTheDocument();
    expect(within(juneRow).getByText("-10.00")).toBeInTheDocument();
  });

  test("shows zero totals for a budget with no transactions", async () => {
    seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    renderWithProviders(<BudgetsPage />);
    const row = await findRow("May");
    await waitFor(() => {
      expect(within(row).getAllByText("0.00")).toHaveLength(3);
    });
  });

  test("totals refresh after creating a budget", async () => {
    renderWithProviders(<BudgetsPage />);
    await userEvent.click(screen.getByRole("button", { name: /new budget/i }));
    await userEvent.type(await screen.findByLabelText(/Name/), "June");
    fireEvent.change(screen.getByLabelText(/Start date/), {
      target: { value: "2026-06-01" },
    });
    fireEvent.change(screen.getByLabelText(/End date/), {
      target: { value: "2026-06-30" },
    });
    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    const row = await findRow("June");
    await waitFor(() => {
      expect(within(row).getAllByText("0.00")).toHaveLength(3);
    });
  });

  test("remaining rows keep their totals after a delete", async () => {
    const may = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    seedBudget({
      name: "June",
      start_date: "2026-06-01",
      end_date: "2026-06-30",
    });
    const expenseCat = seedCategory({ name: "Food", kind: "expense" });
    seedTransaction({
      budget_id: may.id,
      category_id: expenseCat.id,
      type: "expense",
      amount: "30.00",
      date: "2026-05-10",
    });

    renderWithProviders(<BudgetsPage />);
    await waitFor(() => {
      expect(within(getRow("May")).getByText("30.00")).toBeInTheDocument();
    });

    const juneRow = getRow("June");
    await userEvent.click(
      within(juneRow).getByRole("button", { name: "Delete" }),
    );
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(
      within(dialog).getByRole("button", { name: "Delete" }),
    );

    await waitFor(() =>
      expect(screen.queryByText("June")).not.toBeInTheDocument(),
    );
    expect(within(getRow("May")).getByText("30.00")).toBeInTheDocument();
  });

  test("surfaces a summary load error and shows no totals for affected rows", async () => {
    seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    server.use(
      http.get(
        "http://localhost:8000/budgets/:id/summary",
        () => HttpResponse.json({ detail: "Summary blew up" }, { status: 500 }),
      ),
    );
    renderWithProviders(<BudgetsPage />);
    expect(await screen.findByText("Summary blew up")).toBeInTheDocument();
    const row = getRow("May");
    expect(within(row).getAllByText("—")).toHaveLength(3);
  });
});
