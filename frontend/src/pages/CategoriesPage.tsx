import {
  Alert,
  Button,
  Group,
  Modal,
  SegmentedControl,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { useState } from "react";

import { ApiError, api } from "../api/client";
import type { Category, CategoryCreate, CategoryKind } from "../api/types";
import { CategoryForm } from "../components/CategoryForm";
import { useApiResource } from "../hooks/useApiResource";

type Filter = "all" | CategoryKind;

export function CategoriesPage() {
  const [filter, setFilter] = useState<Filter>("all");
  const categories = useApiResource(
    () => api.listCategories(filter === "all" ? undefined : filter),
    [filter],
  );

  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string>();
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState<Category | null>(null);
  const [deleteError, setDeleteError] = useState<string>();

  async function handleCreate(data: CategoryCreate) {
    setSubmitting(true);
    setFormError(undefined);
    try {
      await api.createCategory(data);
      setCreating(false);
      categories.reload();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Unexpected error");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete() {
    if (!deleting) {
      return;
    }
    setDeleteError(undefined);
    try {
      await api.deleteCategory(deleting.id);
      setDeleting(null);
      categories.reload();
    } catch (err) {
      setDeleteError(
        err instanceof ApiError ? err.message : "Unexpected error",
      );
    }
  }

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Categories</Title>
        <Button
          onClick={() => {
            setFormError(undefined);
            setCreating(true);
          }}
        >
          New category
        </Button>
      </Group>

      <SegmentedControl
        value={filter}
        onChange={(value) => setFilter(value as Filter)}
        data={[
          { label: "All", value: "all" },
          { label: "Income", value: "income" },
          { label: "Expense", value: "expense" },
        ]}
      />

      {categories.error && <Alert color="red">{categories.error}</Alert>}
      {!categories.loading && categories.data?.length === 0 && (
        <Text c="dimmed">No categories.</Text>
      )}

      {categories.data && categories.data.length > 0 && (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Kind</Table.Th>
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {categories.data.map((category) => (
              <Table.Tr key={category.id}>
                <Table.Td>{category.name}</Table.Td>
                <Table.Td>{category.kind}</Table.Td>
                <Table.Td>
                  <Group justify="flex-end">
                    <Button
                      variant="subtle"
                      color="red"
                      size="xs"
                      onClick={() => {
                        setDeleteError(undefined);
                        setDeleting(category);
                      }}
                    >
                      Delete
                    </Button>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}

      <Modal
        opened={creating}
        onClose={() => setCreating(false)}
        title="New category"
      >
        <CategoryForm
          error={formError}
          submitting={submitting}
          onSubmit={handleCreate}
        />
      </Modal>

      <Modal
        opened={deleting !== null}
        onClose={() => setDeleting(null)}
        title="Delete category"
      >
        <Text>Delete category “{deleting?.name}”?</Text>
        {deleteError && (
          <Alert color="red" mt="sm">
            {deleteError}
          </Alert>
        )}
        <Group justify="flex-end" mt="md">
          <Button variant="default" onClick={() => setDeleting(null)}>
            Cancel
          </Button>
          <Button color="red" onClick={handleDelete}>
            Delete
          </Button>
        </Group>
      </Modal>
    </Stack>
  );
}
