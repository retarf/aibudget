import { fireEvent, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ApiError } from "../api/client";
import type { Category, CategoryCreate } from "../api/types";
import { TransactionForm } from "../components/TransactionForm";
import { renderWithProviders } from "../test-utils";

const RENT: Category = { id: 7, name: "Rent", kind: "expense" };

/** Pick the transaction Type from the SegmentedControl. */
async function chooseType(value: "Income" | "Expense") {
  await userEvent.click(screen.getByText(value));
}

describe("TransactionForm", () => {
  test("disables the category picker until a Type is chosen", async () => {
    renderWithProviders(
      <TransactionForm
        categories={[RENT]}
        onSubmit={() => {}}
        onCreateCategory={async () => RENT}
      />,
    );
    expect(screen.getByLabelText("Category")).toBeDisabled();
    await chooseType("Expense");
    expect(screen.getByLabelText("Category")).toBeEnabled();
  });

  test("creates a category inline through the picker and selects it", async () => {
    const onCreateCategory = jest.fn<Promise<Category>, [CategoryCreate]>(
      async () => RENT,
    );
    renderWithProviders(
      <TransactionForm
        categories={[]}
        onSubmit={() => {}}
        onCreateCategory={onCreateCategory}
      />,
    );

    await chooseType("Expense");
    await userEvent.type(screen.getByLabelText("Category"), "Rent");
    fireEvent.keyDown(screen.getByLabelText("Category"), { key: "Enter" });

    await waitFor(() =>
      expect(onCreateCategory).toHaveBeenCalledWith({
        name: "Rent",
        kind: "expense",
      }),
    );
    await waitFor(() =>
      expect(screen.getByLabelText("Category")).toHaveValue("Rent"),
    );
  });

  test("a new category inherits the chosen Type's kind", async () => {
    const onCreateCategory = jest.fn<Promise<Category>, [CategoryCreate]>(
      async (data) => ({ id: 5, ...data }),
    );
    renderWithProviders(
      <TransactionForm
        categories={[]}
        onSubmit={() => {}}
        onCreateCategory={onCreateCategory}
      />,
    );

    await chooseType("Income");
    await userEvent.type(screen.getByLabelText("Category"), "Salary");
    fireEvent.keyDown(screen.getByLabelText("Category"), { key: "Enter" });

    await waitFor(() =>
      expect(onCreateCategory).toHaveBeenCalledWith({
        name: "Salary",
        kind: "income",
      }),
    );
  });

  test("reports a duplicate category inline", async () => {
    const onCreateCategory = jest.fn<Promise<Category>, [CategoryCreate]>(
      async () => {
        throw new ApiError(
          409,
          "A category with this name already exists for this kind",
        );
      },
    );
    renderWithProviders(
      <TransactionForm
        categories={[]}
        onSubmit={() => {}}
        onCreateCategory={onCreateCategory}
      />,
    );

    await chooseType("Expense");
    await userEvent.type(screen.getByLabelText("Category"), "Food");
    fireEvent.keyDown(screen.getByLabelText("Category"), { key: "Enter" });

    expect(await screen.findByText(/already exists/i)).toBeInTheDocument();
  });
});
