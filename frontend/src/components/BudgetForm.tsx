import { Button, Group, Stack, TextInput } from "@mantine/core";
import { type FormEvent, useState } from "react";

import type { Budget, BudgetInput } from "../api/types";

interface Props {
  initial?: Budget;
  error?: string;
  submitting?: boolean;
  onSubmit: (data: BudgetInput) => void;
}

/** Create/edit form for a budget. */
export function BudgetForm({ initial, error, submitting, onSubmit }: Props) {
  const [name, setName] = useState(initial?.name ?? "");
  const [startDate, setStartDate] = useState(initial?.start_date ?? "");
  const [endDate, setEndDate] = useState(initial?.end_date ?? "");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({ name, start_date: startDate, end_date: endDate });
  }

  return (
    <form onSubmit={handleSubmit}>
      <Stack>
        <TextInput
          label="Name"
          value={name}
          onChange={(e) => setName(e.currentTarget.value)}
          required
        />
        <TextInput
          label="Start date"
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.currentTarget.value)}
          required
        />
        <TextInput
          label="End date"
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.currentTarget.value)}
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
