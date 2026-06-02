import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import type { Category } from "../api/types";
import {
  seedAllocation,
  seedBudget,
  seedCategory,
  seedTemplate,
} from "../mocks/handlers";
import { AllocationPanel } from "../components/AllocationPanel";
import { renderWithProviders } from "../test-utils";

const MAY = {
  name: "May",
  start_date: "2026-05-01",
  end_date: "2026-05-31",
};

const noopCreate = async (): Promise<Category> => ({
  id: 0,
  name: "",
  kind: "expense",
});

describe("AllocationPanel", () => {
  test("shows empty state when there are no allocations", async () => {
    const budget = seedBudget(MAY);
    renderWithProviders(
      <AllocationPanel
        budgetId={budget.id}
        categories={[]}
        onCreateCategory={noopCreate}
      />,
    );
    expect(await screen.findByText(/no allocations yet/i)).toBeInTheDocument();
  });

  test("lists existing allocations", async () => {
    const budget = seedBudget(MAY);
    const category = seedCategory({ name: "Food", kind: "expense" });
    seedAllocation({
      budget_id: budget.id,
      category_id: category.id,
      planned_amount: "100.00",
    });
    renderWithProviders(
      <AllocationPanel
        budgetId={budget.id}
        categories={[category]}
        onCreateCategory={noopCreate}
      />,
    );
    expect(await screen.findByText("Food")).toBeInTheDocument();
    expect(screen.getByText("100.00")).toBeInTheDocument();
  });

  test("deletes an allocation", async () => {
    const budget = seedBudget(MAY);
    const category = seedCategory({ name: "Food", kind: "expense" });
    seedAllocation({
      budget_id: budget.id,
      category_id: category.id,
      planned_amount: "100.00",
    });
    renderWithProviders(
      <AllocationPanel
        budgetId={budget.id}
        categories={[category]}
        onCreateCategory={noopCreate}
      />,
    );
    await screen.findByText("100.00");
    await userEvent.click(
      screen.getByRole("button", { name: /delete allocation/i }),
    );
    await waitFor(() =>
      expect(screen.queryByText("100.00")).not.toBeInTheDocument(),
    );
  });

  test("opens the apply-template modal with the available templates", async () => {
    const budget = seedBudget(MAY);
    const food = seedCategory({ name: "Food", kind: "expense" });
    seedTemplate("Monthly", [
      { category_id: food.id, planned_amount: "200.00" },
    ]);
    renderWithProviders(
      <AllocationPanel
        budgetId={budget.id}
        categories={[food]}
        onCreateCategory={noopCreate}
      />,
    );
    await screen.findByText(/no allocations yet/i);

    await userEvent.click(
      screen.getByRole("button", { name: /apply template/i }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByLabelText("Template")).toBeInTheDocument();
    expect(
      within(dialog).getByRole("button", { name: "Apply" }),
    ).toBeDisabled();
  });

  test("the category picker is gated by the income/expense toggle", async () => {
    const budget = seedBudget(MAY);
    const food = seedCategory({ name: "Food", kind: "expense" });
    renderWithProviders(
      <AllocationPanel
        budgetId={budget.id}
        categories={[food]}
        onCreateCategory={noopCreate}
      />,
    );
    await screen.findByText(/no allocations yet/i);

    await userEvent.click(
      screen.getByRole("button", { name: /add allocation/i }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByLabelText("Category")).toBeDisabled();

    await userEvent.click(within(dialog).getByText("Expense"));
    expect(within(dialog).getByLabelText("Category")).toBeEnabled();
  });

  test("creates a category inline from the allocation form, inheriting the kind", async () => {
    const onCreateCategory = jest.fn(
      async (): Promise<Category> => ({ id: 99, name: "Rent", kind: "expense" }),
    );
    const budget = seedBudget(MAY);
    renderWithProviders(
      <AllocationPanel
        budgetId={budget.id}
        categories={[]}
        onCreateCategory={onCreateCategory}
      />,
    );
    await screen.findByText(/no allocations yet/i);

    await userEvent.click(
      screen.getByRole("button", { name: /add allocation/i }),
    );
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(within(dialog).getByText("Expense"));
    await userEvent.type(within(dialog).getByLabelText("Category"), "Rent");
    fireEvent.keyDown(within(dialog).getByLabelText("Category"), {
      key: "Enter",
    });

    await waitFor(() =>
      expect(onCreateCategory).toHaveBeenCalledWith({
        name: "Rent",
        kind: "expense",
      }),
    );
  });
});
