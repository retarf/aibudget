import { fireEvent, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ApiError } from "../api/client";
import type { Category, CategoryCreate } from "../api/types";
import { TransactionForm } from "../components/TransactionForm";
import { renderWithProviders } from "../test-utils";

const RENT: Category = { id: 7, name: "Rent", kind: "expense" };

describe("inline category creation", () => {
  test("creates a category inline and selects it", async () => {
    const onCreateCategory = jest.fn<Promise<Category>, [CategoryCreate]>(
      async () => RENT,
    );
    renderWithProviders(
      <TransactionForm
        categories={[RENT]}
        onSubmit={() => {}}
        onCreateCategory={onCreateCategory}
      />,
    );

    await userEvent.click(
      screen.getByRole("button", { name: /new category/i }),
    );
    await userEvent.type(await screen.findByLabelText(/^Name/), "Rent");
    await userEvent.click(
      screen.getByRole("button", { name: /add category/i }),
    );

    await waitFor(() =>
      expect(onCreateCategory).toHaveBeenCalledWith({
        name: "Rent",
        kind: "expense",
      }),
    );
    await waitFor(() =>
      expect(
        screen.getByRole("combobox", { name: /Category/ }),
      ).toHaveValue("Rent (expense)"),
    );
  });

  test("keeps the other transaction fields across an inline create", async () => {
    const onCreateCategory = jest.fn<Promise<Category>, [CategoryCreate]>(
      async () => RENT,
    );
    renderWithProviders(
      <TransactionForm
        categories={[RENT]}
        onSubmit={() => {}}
        onCreateCategory={onCreateCategory}
      />,
    );

    fireEvent.change(screen.getByLabelText(/^Date/), {
      target: { value: "2026-05-10" },
    });
    await userEvent.click(
      screen.getByRole("button", { name: /new category/i }),
    );
    await userEvent.type(await screen.findByLabelText(/^Name/), "Rent");
    await userEvent.click(
      screen.getByRole("button", { name: /add category/i }),
    );

    await waitFor(() => expect(onCreateCategory).toHaveBeenCalled());
    expect(screen.getByLabelText(/^Date/)).toHaveValue("2026-05-10");
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

    await userEvent.click(
      screen.getByRole("button", { name: /new category/i }),
    );
    await userEvent.type(await screen.findByLabelText(/^Name/), "Food");
    await userEvent.click(
      screen.getByRole("button", { name: /add category/i }),
    );

    expect(
      await screen.findByText(/already exists/i),
    ).toBeInTheDocument();
  });
});
