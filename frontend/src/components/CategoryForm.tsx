import { Button, Group, Select, Stack, TextInput } from "@mantine/core";
import { type FormEvent, useState } from "react";

import type { CategoryCreate, CategoryKind } from "../api/types";

interface Props {
  error?: string;
  submitting?: boolean;
  onSubmit: (data: CategoryCreate) => void;
}

/** Create form for a category. */
export function CategoryForm({ error, submitting, onSubmit }: Props) {
  const [name, setName] = useState("");
  const [kind, setKind] = useState<CategoryKind>("expense");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({ name, kind });
  }

  return (
    <form onSubmit={handleSubmit}>
      <Stack>
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
        <Group justify="flex-end">
          <Button type="submit" loading={submitting}>
            Save
          </Button>
        </Group>
      </Stack>
    </form>
  );
}
