import { Button, Group, NumberInput, Select, Stack, TextInput } from "@mantine/core";
import { type FormEvent, useState } from "react";

import type {
  Category,
  Transaction,
  TransactionInput,
  TransactionType,
} from "../api/types";

interface Props {
  categories: Category[];
  initial?: Transaction;
  error?: string;
  submitting?: boolean;
  onSubmit: (data: TransactionInput) => void;
}

/** Create/edit form for a transaction within a budget. */
export function TransactionForm({
  categories,
  initial,
  error,
  submitting,
  onSubmit,
}: Props) {
  const [type, setType] = useState<TransactionType>(initial?.type ?? "expense");
  const [amount, setAmount] = useState<string>(initial?.amount ?? "");
  const [date, setDate] = useState(initial?.date ?? "");
  const [categoryId, setCategoryId] = useState<string | null>(
    initial ? String(initial.category_id) : null,
  );

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({
      type,
      amount: String(amount),
      date,
      category_id: Number(categoryId),
    });
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
        <Group justify="flex-end">
          <Button type="submit" loading={submitting}>
            Save
          </Button>
        </Group>
      </Stack>
    </form>
  );
}
