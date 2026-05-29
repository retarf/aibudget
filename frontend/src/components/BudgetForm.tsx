import { Button, Group, Select, Stack, TextInput } from "@mantine/core";
import { type FormEvent, useEffect, useState } from "react";

import { api } from "../api/client";
import type { Budget, BudgetInput, Template } from "../api/types";

interface Props {
  initial?: Budget;
  error?: string;
  submitting?: boolean;
  onSubmit: (data: BudgetInput, templateId?: number) => void;
}

/** Create/edit form for a budget. */
export function BudgetForm({ initial, error, submitting, onSubmit }: Props) {
  const [name, setName] = useState(initial?.name ?? "");
  const [startDate, setStartDate] = useState(initial?.start_date ?? "");
  const [endDate, setEndDate] = useState(initial?.end_date ?? "");
  const [templateId, setTemplateId] = useState<string | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);

  const isCreating = initial === undefined;

  useEffect(() => {
    if (!isCreating) return;
    let cancelled = false;
    api
      .listTemplates()
      .then((list) => {
        if (!cancelled) setTemplates(list);
      })
      .catch(() => {
        // Template selector is optional; failing to load it shouldn't block
        // budget creation.
      });
    return () => {
      cancelled = true;
    };
  }, [isCreating]);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit(
      { name, start_date: startDate, end_date: endDate },
      templateId ? Number(templateId) : undefined,
    );
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
        {isCreating && templates.length > 0 && (
          <Select
            label="Start from a template"
            placeholder="No template"
            data={templates.map((t) => ({
              value: String(t.id),
              label: t.name,
            }))}
            value={templateId}
            onChange={setTemplateId}
            clearable
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
