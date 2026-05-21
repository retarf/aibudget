import { Button, Group, Paper, Select, Stack, Text, TextInput } from "@mantine/core";
import { useState } from "react";

import type { CategoryCreate, CategoryKind } from "../api/types";

interface Props {
  error?: string;
  submitting?: boolean;
  onCreate: (data: CategoryCreate) => void;
  onCancel: () => void;
}

/**
 * Inline mini-form for creating a category without leaving the transaction
 * form. Deliberately not a `<form>` element — it is rendered inside the
 * transaction form's `<form>`, and nested forms are invalid HTML.
 */
export function InlineCategoryCreator({
  error,
  submitting,
  onCreate,
  onCancel,
}: Props) {
  const [name, setName] = useState("");
  const [kind, setKind] = useState<CategoryKind>("expense");

  return (
    <Paper withBorder p="sm">
      <Stack gap="xs">
        <Text size="sm" fw={500}>
          New category
        </Text>
        <TextInput
          label="Name"
          value={name}
          onChange={(e) => setName(e.currentTarget.value)}
          error={error}
          required
        />
        <Select
          label="Kind"
          data={["income", "expense"]}
          value={kind}
          onChange={(value) => setKind((value as CategoryKind) ?? "expense")}
          allowDeselect={false}
        />
        <Group justify="flex-end" gap="xs">
          <Button variant="default" size="xs" type="button" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            size="xs"
            type="button"
            loading={submitting}
            disabled={name.trim() === ""}
            onClick={() => onCreate({ name, kind })}
          >
            Add category
          </Button>
        </Group>
      </Stack>
    </Paper>
  );
}
