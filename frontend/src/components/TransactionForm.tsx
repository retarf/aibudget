import {
  Button,
  Group,
  NumberInput,
  SegmentedControl,
  Stack,
  TextInput,
} from "@mantine/core";
import { type FormEvent, useState } from "react";

import type {
  Category,
  CategoryCreate,
  Transaction,
  TransactionInput,
  TransactionType,
} from "../api/types";
import { CategoryCombobox } from "./CategoryCombobox";

interface Props {
  categories: Category[];
  initial?: Transaction;
  error?: string;
  submitting?: boolean;
  onSubmit: (data: TransactionInput) => void;
  /** Creates a category inline from the category picker. */
  onCreateCategory: (data: CategoryCreate) => Promise<Category>;
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
  const [type, setType] = useState<TransactionType | null>(
    initial?.type ?? null,
  );
  const [amount, setAmount] = useState<string>(initial?.amount ?? "");
  const [date, setDate] = useState(initial?.date ?? "");
  const [categoryId, setCategoryId] = useState<number | null>(
    initial?.category_id ?? null,
  );

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (type == null || categoryId == null) {
      return;
    }
    onSubmit({
      type,
      amount: String(amount),
      date,
      category_id: categoryId,
    });
  }

  return (
    <form onSubmit={handleSubmit}>
      <Stack>
        <SegmentedControl
          aria-label="Type"
          data={[
            { label: "Income", value: "income" },
            { label: "Expense", value: "expense" },
          ]}
          value={type ?? ""}
          onChange={(value) => setType(value as TransactionType)}
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
        <CategoryCombobox
          categories={categories}
          kind={type}
          value={categoryId}
          onChange={setCategoryId}
          onCreateCategory={onCreateCategory}
          error={error}
        />

        <Group justify="flex-end">
          <Button
            type="submit"
            loading={submitting}
            disabled={type == null || categoryId == null}
          >
            Save
          </Button>
        </Group>
      </Stack>
    </form>
  );
}
