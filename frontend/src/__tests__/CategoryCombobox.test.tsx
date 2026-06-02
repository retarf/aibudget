import { fireEvent, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";

import { ApiError } from "../api/client";
import { CategoryCombobox } from "../components/CategoryCombobox";
import type { Category, CategoryCreate, CategoryKind } from "../api/types";
import { renderWithProviders } from "../test-utils";

const FOOD: Category = { id: 1, name: "Food", kind: "expense" };
const SALARY: Category = { id: 2, name: "Salary", kind: "income" };

/** Controlled wrapper exposing kind/value state and an onChange spy. */
function Harness({
  categories,
  initialKind = null,
  onCreateCategory,
  onChangeSpy,
}: {
  categories: Category[];
  initialKind?: CategoryKind | null;
  onCreateCategory: (data: CategoryCreate) => Promise<Category>;
  onChangeSpy?: (value: number | null) => void;
}) {
  const [kind, setKind] = useState<CategoryKind | null>(initialKind);
  const [value, setValue] = useState<number | null>(null);
  return (
    <>
      <button type="button" onClick={() => setKind("income")}>
        set income
      </button>
      <button type="button" onClick={() => setKind("expense")}>
        set expense
      </button>
      <CategoryCombobox
        categories={categories}
        kind={kind}
        value={value}
        onChange={(v) => {
          setValue(v);
          onChangeSpy?.(v);
        }}
        onCreateCategory={onCreateCategory}
      />
    </>
  );
}

const noopCreate = async (): Promise<Category> => FOOD;

function input() {
  return screen.getByLabelText("Category");
}

describe("CategoryCombobox", () => {
  test("is disabled until a kind is chosen, then enabled", async () => {
    renderWithProviders(
      <Harness categories={[FOOD, SALARY]} onCreateCategory={noopCreate} />,
    );
    expect(input()).toBeDisabled();

    await userEvent.click(screen.getByRole("button", { name: "set expense" }));
    expect(input()).toBeEnabled();
  });

  test("offers only categories of the active kind", async () => {
    renderWithProviders(
      <Harness
        categories={[FOOD, SALARY]}
        initialKind="expense"
        onCreateCategory={noopCreate}
      />,
    );
    await userEvent.click(input());
    expect(await screen.findByText("Food")).toBeInTheDocument();
    expect(screen.queryByText("Salary")).not.toBeInTheDocument();
  });

  test("Tab accepts the best match", async () => {
    const onChangeSpy = jest.fn();
    renderWithProviders(
      <Harness
        categories={[FOOD, SALARY]}
        initialKind="expense"
        onCreateCategory={noopCreate}
        onChangeSpy={onChangeSpy}
      />,
    );
    await userEvent.type(input(), "Foo");
    fireEvent.keyDown(input(), { key: "Tab" });
    expect(onChangeSpy).toHaveBeenLastCalledWith(FOOD.id);
  });

  test("Enter selects an exact match without creating", async () => {
    const onCreateCategory = jest.fn(noopCreate);
    const onChangeSpy = jest.fn();
    renderWithProviders(
      <Harness
        categories={[FOOD, SALARY]}
        initialKind="expense"
        onCreateCategory={onCreateCategory}
        onChangeSpy={onChangeSpy}
      />,
    );
    await userEvent.type(input(), "Food");
    fireEvent.keyDown(input(), { key: "Enter" });
    expect(onChangeSpy).toHaveBeenLastCalledWith(FOOD.id);
    expect(onCreateCategory).not.toHaveBeenCalled();
  });

  test("Enter creates when no category matches, inheriting the kind", async () => {
    const created: Category = { id: 9, name: "Rent", kind: "expense" };
    const onCreateCategory = jest.fn(async () => created);
    const onChangeSpy = jest.fn();
    renderWithProviders(
      <Harness
        categories={[FOOD]}
        initialKind="expense"
        onCreateCategory={onCreateCategory}
        onChangeSpy={onChangeSpy}
      />,
    );
    await userEvent.type(input(), "Rent");
    fireEvent.keyDown(input(), { key: "Enter" });
    await waitFor(() =>
      expect(onCreateCategory).toHaveBeenCalledWith({
        name: "Rent",
        kind: "expense",
      }),
    );
    await waitFor(() => expect(onChangeSpy).toHaveBeenLastCalledWith(9));
  });

  test("a real Enter keypress creates exactly once (no duplicate 409)", async () => {
    const created: Category = { id: 9, name: "Rent", kind: "expense" };
    const onCreateCategory = jest.fn(async () => created);
    renderWithProviders(
      <Harness
        categories={[]}
        initialKind="expense"
        onCreateCategory={onCreateCategory}
      />,
    );
    await userEvent.click(input());
    await userEvent.type(input(), "Rent");
    await userEvent.keyboard("{Enter}");
    await waitFor(() => expect(onCreateCategory).toHaveBeenCalled());
    expect(onCreateCategory).toHaveBeenCalledTimes(1);
  });

  test("the create row creates with the mouse", async () => {
    const created: Category = { id: 9, name: "Rent", kind: "expense" };
    const onCreateCategory = jest.fn(async () => created);
    renderWithProviders(
      <Harness
        categories={[FOOD]}
        initialKind="expense"
        onCreateCategory={onCreateCategory}
      />,
    );
    await userEvent.type(input(), "Rent");
    await userEvent.click(await screen.findByText(/Create/));
    await waitFor(() =>
      expect(onCreateCategory).toHaveBeenCalledWith({
        name: "Rent",
        kind: "expense",
      }),
    );
  });

  test("surfaces an API rejection on create", async () => {
    const onCreateCategory = jest.fn(async () => {
      throw new ApiError(409, "already exists for this kind");
    });
    renderWithProviders(
      <Harness
        categories={[]}
        initialKind="expense"
        onCreateCategory={onCreateCategory}
      />,
    );
    await userEvent.type(input(), "Rent");
    fireEvent.keyDown(input(), { key: "Enter" });
    expect(await screen.findByText(/already exists/i)).toBeInTheDocument();
  });

  test("clears a selection whose kind no longer matches when the kind changes", async () => {
    const onChangeSpy = jest.fn();
    renderWithProviders(
      <Harness
        categories={[FOOD, SALARY]}
        initialKind="expense"
        onCreateCategory={noopCreate}
        onChangeSpy={onChangeSpy}
      />,
    );
    await userEvent.type(input(), "Food");
    fireEvent.keyDown(input(), { key: "Enter" });
    expect(input()).toHaveValue("Food");

    await userEvent.click(screen.getByRole("button", { name: "set income" }));
    await waitFor(() => expect(input()).toHaveValue(""));
    expect(onChangeSpy).toHaveBeenLastCalledWith(null);
  });
});
