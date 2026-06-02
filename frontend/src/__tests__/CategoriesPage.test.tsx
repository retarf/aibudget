import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";

import { seedBudget, seedCategory, seedTransaction } from "../mocks/handlers";
import { server } from "../mocks/server";
import { CategoriesPage } from "../pages/CategoriesPage";
import { renderWithProviders } from "../test-utils";

describe("category pages", () => {
  test("lists categories", async () => {
    seedCategory({ name: "Food", kind: "expense" });
    renderWithProviders(<CategoriesPage />);
    expect(await screen.findByText("Food")).toBeInTheDocument();
  });

  test("filters categories by kind", async () => {
    seedCategory({ name: "Food", kind: "expense" });
    seedCategory({ name: "Salary", kind: "income" });
    renderWithProviders(<CategoriesPage />);
    await screen.findByText("Food");
    await userEvent.click(screen.getByText("Income"));
    await waitFor(() =>
      expect(screen.queryByText("Food")).not.toBeInTheDocument(),
    );
    expect(screen.getByText("Salary")).toBeInTheDocument();
  });

  test("creates a category", async () => {
    renderWithProviders(<CategoriesPage />);
    await userEvent.click(
      screen.getByRole("button", { name: /new category/i }),
    );
    const nameInput = await screen.findByLabelText(/Name/);
    await userEvent.type(nameInput, "Rent");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Rent")).toBeInTheDocument();
  });

  test("surfaces the duplicate-category error", async () => {
    seedCategory({ name: "Food", kind: "expense" });
    renderWithProviders(<CategoriesPage />);
    await screen.findByText("Food");
    await userEvent.click(
      screen.getByRole("button", { name: /new category/i }),
    );
    const nameInput = await screen.findByLabelText(/Name/);
    await userEvent.type(nameInput, "Food");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText(/already exists/i)).toBeInTheDocument();
  });

  test("an unused category can be deleted", async () => {
    seedCategory({ name: "Rent", kind: "expense" });
    renderWithProviders(<CategoriesPage />);
    await screen.findByText("Rent");
    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(
      within(dialog).getByRole("button", { name: "Delete" }),
    );
    await waitFor(() =>
      expect(screen.queryByText("Rent")).not.toBeInTheDocument(),
    );
  });

  function seedFoodWithTransaction() {
    const category = seedCategory({ name: "Food", kind: "expense" });
    const budget = seedBudget({
      name: "May",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    });
    seedTransaction({
      budget_id: budget.id,
      category_id: category.id,
      type: "expense",
      amount: "5.00",
      date: "2026-05-10",
    });
  }

  test("an in-use category offers Erase history, not Delete", async () => {
    seedFoodWithTransaction();
    renderWithProviders(<CategoriesPage />);
    await screen.findByText("Food");
    expect(
      screen.getByRole("button", { name: /erase history/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Delete" }),
    ).not.toBeInTheDocument();
  });

  test("erasing history shows impact counts and makes the category deletable", async () => {
    seedFoodWithTransaction();
    renderWithProviders(<CategoriesPage />);
    await screen.findByText("Food");

    await userEvent.click(
      screen.getByRole("button", { name: /erase history/i }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(dialog).toHaveTextContent("1 transactions");

    await userEvent.click(
      within(dialog).getByRole("button", { name: /erase history/i }),
    );

    expect(
      await screen.findByRole("button", { name: "Delete" }),
    ).toBeInTheDocument();
  });

  test("offers no destructive action when usage is unknown (stale backend)", async () => {
    // Simulate an older gateway that returns categories without usage fields.
    server.use(
      http.get("http://localhost:8000/categories", () =>
        HttpResponse.json([{ id: 1, name: "Food", kind: "expense" }]),
      ),
    );
    renderWithProviders(<CategoriesPage />);
    await screen.findByText("Food");
    expect(
      screen.queryByRole("button", { name: "Delete" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /erase history/i }),
    ).not.toBeInTheDocument();
  });
});
