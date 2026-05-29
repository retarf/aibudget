import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import {
  seedAllocation,
  seedBudget,
  seedCategory,
  seedTemplate,
} from "../mocks/handlers";
import { AllocationPanel } from "../components/AllocationPanel";
import { renderWithProviders } from "../test-utils";

describe("AllocationPanel", () => {
  test("shows empty state when there are no allocations", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    renderWithProviders(
      <AllocationPanel budgetId={budget.id} categories={[]} />,
    );
    expect(await screen.findByText(/no allocations yet/i)).toBeInTheDocument();
  });

  test("lists existing allocations", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
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
      />,
    );
    expect(await screen.findByText("Food")).toBeInTheDocument();
    expect(screen.getByText("100.00")).toBeInTheDocument();
  });

  test("deletes an allocation", async () => {
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
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
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    const food = seedCategory({ name: "Food", kind: "expense" });
    seedTemplate("Monthly", [
      { category_id: food.id, planned_amount: "200.00" },
    ]);
    renderWithProviders(
      <AllocationPanel budgetId={budget.id} categories={[food]} />,
    );
    await screen.findByText(/no allocations yet/i);

    await userEvent.click(
      screen.getByRole("button", { name: /apply template/i }),
    );
    const dialog = await screen.findByRole("dialog");
    // The template selector is wired up and disabled by default until a
    // template is picked.
    expect(within(dialog).getByLabelText("Template")).toBeInTheDocument();
    expect(
      within(dialog).getByRole("button", { name: "Apply" }),
    ).toBeDisabled();
  });
});
