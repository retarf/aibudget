import { Button, Group, NumberInput, Select, Stack, TextInput } from "@mantine/core";
import { type FormEvent, useState } from "react";

import { ApiError } from "../api/client";
import type {
  Category,
  CategoryCreate,
  Transaction,
  TransactionInput,
  TransactionType,
} from "../api/types";
import { InlineCategoryCreator } from "./InlineCategoryCreator";

interface Props {
  categories: Category[];
  initial?: Transaction;
  error?: string;
  submitting?: boolean;
  onSubmit: (data: TransactionInput) => void;
  /** When provided, the form can create a new category inline. */
  onCreateCategory?: (data: CategoryCreate) => Promise<Category>;
}

/** Create/edit form for a transaction within a budget. */
export function TransactionForm({
  categories,
  initial,
  error,
  submitting,
  onSubmit,
  onCreateCategory,
}: Props) {
  const [type, setType] = useState<TransactionType>(initial?.type ?? "expense");
  const [amount, setAmount] = useState<string>(initial?.amount ?? "");
  const [date, setDate] = useState(initial?.date ?? "");
  const [categoryId, setCategoryId] = useState<string | null>(
    initial ? String(initial.category_id) : null,
  );

  const [addingCategory, setAddingCategory] = useState(false);
  const [creatingCategory, setCreatingCategory] = useState(false);
  const [categoryError, setCategoryError] = useState<string>();

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({
      type,
      amount: String(amount),
      date,
      category_id: Number(categoryId),
    });
  }

  async function handleCreateCategory(data: CategoryCreate) {
    if (!onCreateCategory) {
      return;
    }
    setCreatingCategory(true);
    setCategoryError(undefined);
    try {
      const created = await onCreateCategory(data);
      // Select the new category; other transaction fields are left untouched.
      setCategoryId(String(created.id));
      setAddingCategory(false);
    } catch (err) {
      setCategoryError(
        err instanceof ApiError ? err.message : "Unexpected error",
      );
    } finally {
      setCreatingCategory(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Stack>
        <Select
          label="Type"
          data={["income", "expense"]}
          value={type}
          onChange={(value) => setType((value as TransactionType) ?? "expense")}
          allowDeselect={false}
        />
        <NumberInput
          label="Amount"
          value={amount}
          onChange={(value) => setAmount(String(value))}
          min={0}
          decimalScale={2}
          required
        />
        <TextInput
          label="Date"
          type="date"
          value={date}
          onChange={(e) => setDate(e.currentTarget.value)}
          required
        />
        <Select
          label="Category"
          placeholder="Select a category"
          data={categories.map((c) => ({
            value: String(c.id),
            label: `${c.name} (${c.kind})`,
          }))}
          value={categoryId}
          onChange={setCategoryId}
          error={error}
          required
        />

        {onCreateCategory && !addingCategory && (
          <Button
            variant="subtle"
            size="xs"
            type="button"
            style={{ alignSelf: "flex-start" }}
            onClick={() => {
              setCategoryError(undefined);
              setAddingCategory(true);
            }}
          >
            + New category
          </Button>
        )}
        {onCreateCategory && addingCategory && (
          <InlineCategoryCreator
            error={categoryError}
            submitting={creatingCategory}
            onCreate={handleCreateCategory}
            onCancel={() => setAddingCategory(false)}
          />
        )}

        <Group justify="flex-end">
          <Button type="submit" loading={submitting}>
            Save
          </Button>
        </Group>
      </Stack>
    </form>
  );
}
