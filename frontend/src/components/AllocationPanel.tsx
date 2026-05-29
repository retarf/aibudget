import {
  ActionIcon,
  Alert,
  Button,
  Group,
  Modal,
  NumberInput,
  Select,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { type FormEvent, useState } from "react";

import { ApiError, api } from "../api/client";
import type { Allocation, Category, Template } from "../api/types";
import { useApiResource } from "../hooks/useApiResource";

interface Props {
  budgetId: number;
  categories: Category[];
  onChange?: () => void;
}

/**
 * Lists, edits, and removes planned allocations for one budget; lets the user
 * apply a template to bulk-create them.
 */
export function AllocationPanel({ budgetId, categories, onChange }: Props) {
  const allocations = useApiResource(
    () => api.listAllocations(budgetId),
    [budgetId],
  );
  const templates = useApiResource(() => api.listTemplates(), []);

  const [adding, setAdding] = useState(false);
  const [addError, setAddError] = useState<string>();
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValue, setEditValue] = useState<string>("");
  const [applyOpen, setApplyOpen] = useState(false);
  const [applyTemplateId, setApplyTemplateId] = useState<string | null>(null);
  const [applyError, setApplyError] = useState<string>();

  function reload() {
    allocations.reload();
    onChange?.();
  }

  function categoryName(categoryId: number): string {
    return (
      categories.find((c) => c.id === categoryId)?.name ?? `#${categoryId}`
    );
  }

  async function handleAdd(
    categoryId: number,
    plannedAmount: string,
  ): Promise<void> {
    setAddError(undefined);
    try {
      await api.createAllocation(budgetId, {
        category_id: categoryId,
        planned_amount: plannedAmount,
      });
      setAdding(false);
      reload();
    } catch (err) {
      setAddError(err instanceof ApiError ? err.message : "Unexpected error");
    }
  }

  async function handleDelete(allocation: Allocation): Promise<void> {
    await api.deleteAllocation(budgetId, allocation.id);
    reload();
  }

  function startEdit(allocation: Allocation): void {
    setEditingId(allocation.id);
    setEditValue(allocation.planned_amount);
  }

  async function saveEdit(allocationId: number): Promise<void> {
    await api.updateAllocation(budgetId, allocationId, {
      planned_amount: editValue,
    });
    setEditingId(null);
    reload();
  }

  async function handleApplyTemplate(): Promise<void> {
    if (!applyTemplateId) return;
    setApplyError(undefined);
    try {
      await api.applyTemplate(budgetId, Number(applyTemplateId));
      setApplyOpen(false);
      setApplyTemplateId(null);
      reload();
    } catch (err) {
      setApplyError(
        err instanceof ApiError ? err.message : "Unexpected error",
      );
    }
  }

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={4}>Planned allocations</Title>
        <Group gap="xs">
          <Button
            variant="default"
            size="xs"
            onClick={() => {
              setApplyError(undefined);
              setApplyOpen(true);
            }}
          >
            Apply template
          </Button>
          <Button
            size="xs"
            onClick={() => {
              setAddError(undefined);
              setAdding(true);
            }}
          >
            Add allocation
          </Button>
        </Group>
      </Group>

      {allocations.error && <Alert color="red">{allocations.error}</Alert>}

      {!allocations.loading && allocations.data?.length === 0 && (
        <Text c="dimmed">No allocations yet.</Text>
      )}

      {allocations.data && allocations.data.length > 0 && (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Category</Table.Th>
              <Table.Th>Planned amount</Table.Th>
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {allocations.data.map((allocation) => (
              <Table.Tr key={allocation.id}>
                <Table.Td>{categoryName(allocation.category_id)}</Table.Td>
                <Table.Td>
                  {editingId === allocation.id ? (
                    <Group gap="xs">
                      <NumberInput
                        size="xs"
                        value={editValue}
                        onChange={(v) => setEditValue(String(v))}
                        min={0}
                        decimalScale={2}
                        fixedDecimalScale
                        aria-label="Planned amount"
                      />
                      <Button
                        size="xs"
                        onClick={() => saveEdit(allocation.id)}
                      >
                        Save
                      </Button>
                      <Button
                        size="xs"
                        variant="default"
                        onClick={() => setEditingId(null)}
                      >
                        Cancel
                      </Button>
                    </Group>
                  ) : (
                    allocation.planned_amount
                  )}
                </Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    {editingId !== allocation.id && (
                      <ActionIcon
                        variant="subtle"
                        size="sm"
                        aria-label="Edit allocation"
                        onClick={() => startEdit(allocation)}
                      >
                        ✎
                      </ActionIcon>
                    )}
                    <ActionIcon
                      variant="subtle"
                      color="red"
                      size="sm"
                      aria-label="Delete allocation"
                      onClick={() => handleDelete(allocation)}
                    >
                      ×
                    </ActionIcon>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}

      <Modal
        opened={adding}
        onClose={() => setAdding(false)}
        title="Add allocation"
      >
        <AddAllocationForm
          categories={categories}
          error={addError}
          onSubmit={handleAdd}
          onCancel={() => setAdding(false)}
        />
      </Modal>

      <Modal
        opened={applyOpen}
        onClose={() => setApplyOpen(false)}
        title="Apply template"
      >
        <Stack>
          {applyError && <Alert color="red">{applyError}</Alert>}
          {templates.data && templates.data.length === 0 && (
            <Text c="dimmed">No templates available.</Text>
          )}
          {templates.data && templates.data.length > 0 && (
            <Select
              label="Template"
              placeholder="Pick a template"
              data={templates.data.map((t: Template) => ({
                value: String(t.id),
                label: t.name,
              }))}
              value={applyTemplateId}
              onChange={setApplyTemplateId}
            />
          )}
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setApplyOpen(false)}>
              Cancel
            </Button>
            <Button
              disabled={!applyTemplateId}
              onClick={handleApplyTemplate}
            >
              Apply
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}

interface AddAllocationFormProps {
  categories: Category[];
  error?: string;
  onSubmit: (categoryId: number, plannedAmount: string) => void;
  onCancel: () => void;
}

function AddAllocationForm({
  categories,
  error,
  onSubmit,
  onCancel,
}: AddAllocationFormProps) {
  const [categoryId, setCategoryId] = useState<string | null>(null);
  const [amount, setAmount] = useState<string>("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!categoryId || !amount) return;
    onSubmit(Number(categoryId), amount);
  }

  return (
    <form onSubmit={handleSubmit}>
      <Stack>
        {error && <Alert color="red">{error}</Alert>}
        <Select
          label="Category"
          placeholder="Pick a category"
          data={categories.map((c) => ({
            value: String(c.id),
            label: `${c.name} (${c.kind})`,
          }))}
          value={categoryId}
          onChange={setCategoryId}
          required
        />
        <NumberInput
          label="Planned amount"
          value={amount}
          onChange={(v) => setAmount(String(v))}
          min={0}
          decimalScale={2}
          fixedDecimalScale
          required
        />
        <Group justify="flex-end">
          <Button variant="default" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit">Add</Button>
        </Group>
      </Stack>
    </form>
  );
}
