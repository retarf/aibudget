import {
  Alert,
  Anchor,
  Button,
  Group,
  Modal,
  NumberInput,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { type FormEvent, useState } from "react";

import { ApiError, api } from "../api/client";
import type { Template, TemplateDetail } from "../api/types";
import { useApiResource } from "../hooks/useApiResource";

export function TemplatesPage() {
  const templates = useApiResource(() => api.listTemplates(), []);
  const categories = useApiResource(() => api.listCategories(), []);

  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string>();
  const [openTemplateId, setOpenTemplateId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState<Template | null>(null);

  async function handleCreate(name: string): Promise<void> {
    setCreateError(undefined);
    try {
      await api.createTemplate(name);
      setCreating(false);
      templates.reload();
    } catch (err) {
      setCreateError(
        err instanceof ApiError ? err.message : "Unexpected error",
      );
    }
  }

  async function handleDelete(): Promise<void> {
    if (!deleting) return;
    await api.deleteTemplate(deleting.id);
    setDeleting(null);
    templates.reload();
  }

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Templates</Title>
        <Button
          onClick={() => {
            setCreateError(undefined);
            setCreating(true);
          }}
        >
          New template
        </Button>
      </Group>

      {templates.error && <Alert color="red">{templates.error}</Alert>}
      {!templates.loading && templates.data?.length === 0 && (
        <Text c="dimmed">No templates yet. Create your first one.</Text>
      )}

      {templates.data && templates.data.length > 0 && (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {templates.data.map((template) => (
              <Table.Tr key={template.id}>
                <Table.Td>
                  <Anchor
                    component="button"
                    type="button"
                    onClick={() => setOpenTemplateId(template.id)}
                  >
                    {template.name}
                  </Anchor>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    <Button
                      variant="subtle"
                      size="xs"
                      onClick={() => setOpenTemplateId(template.id)}
                    >
                      Open
                    </Button>
                    <Button
                      variant="subtle"
                      color="red"
                      size="xs"
                      onClick={() => setDeleting(template)}
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
        title="New template"
      >
        <CreateTemplateForm
          error={createError}
          onSubmit={handleCreate}
          onCancel={() => setCreating(false)}
        />
      </Modal>

      <Modal
        opened={openTemplateId !== null}
        onClose={() => setOpenTemplateId(null)}
        title="Template details"
        size="lg"
      >
        {openTemplateId !== null && (
          <TemplateDetailView
            templateId={openTemplateId}
            categories={categories.data ?? []}
          />
        )}
      </Modal>

      <Modal
        opened={deleting !== null}
        onClose={() => setDeleting(null)}
        title="Delete template"
      >
        <Text>Delete template “{deleting?.name}”? All line items are removed.</Text>
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

interface CreateTemplateFormProps {
  error?: string;
  onSubmit: (name: string) => void;
  onCancel: () => void;
}

function CreateTemplateForm({
  error,
  onSubmit,
  onCancel,
}: CreateTemplateFormProps) {
  const [name, setName] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    onSubmit(name.trim());
  }

  return (
    <form onSubmit={handleSubmit}>
      <Stack>
        {error && <Alert color="red">{error}</Alert>}
        <TextInput
          label="Name"
          value={name}
          onChange={(e) => setName(e.currentTarget.value)}
          required
        />
        <Group justify="flex-end">
          <Button variant="default" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit">Create</Button>
        </Group>
      </Stack>
    </form>
  );
}

interface TemplateDetailViewProps {
  templateId: number;
  categories: { id: number; name: string; kind: string }[];
}

function TemplateDetailView({
  templateId,
  categories,
}: TemplateDetailViewProps) {
  const template = useApiResource<TemplateDetail>(
    () => api.getTemplate(templateId),
    [templateId],
  );
  const [addCategoryId, setAddCategoryId] = useState<string | null>(null);
  const [addAmount, setAddAmount] = useState<string>("");
  const [addError, setAddError] = useState<string>();

  function categoryName(categoryId: number): string {
    return (
      categories.find((c) => c.id === categoryId)?.name ?? `#${categoryId}`
    );
  }

  async function handleAdd(event: FormEvent) {
    event.preventDefault();
    if (!addCategoryId || !addAmount) return;
    setAddError(undefined);
    try {
      await api.addTemplateItem(templateId, {
        category_id: Number(addCategoryId),
        planned_amount: addAmount,
      });
      setAddCategoryId(null);
      setAddAmount("");
      template.reload();
    } catch (err) {
      setAddError(err instanceof ApiError ? err.message : "Unexpected error");
    }
  }

  async function handleDeleteItem(itemId: number) {
    await api.deleteTemplateItem(templateId, itemId);
    template.reload();
  }

  return (
    <Stack>
      {template.error && <Alert color="red">{template.error}</Alert>}
      {template.data && (
        <>
          <Title order={4}>{template.data.name}</Title>

          {template.data.items.length === 0 ? (
            <Text c="dimmed">No line items yet.</Text>
          ) : (
            <Table>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Category</Table.Th>
                  <Table.Th>Planned amount</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {template.data.items.map((item) => (
                  <Table.Tr key={item.id}>
                    <Table.Td>{categoryName(item.category_id)}</Table.Td>
                    <Table.Td>{item.planned_amount}</Table.Td>
                    <Table.Td>
                      <Group justify="flex-end">
                        <Button
                          variant="subtle"
                          color="red"
                          size="xs"
                          onClick={() => handleDeleteItem(item.id)}
                        >
                          Remove
                        </Button>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          )}

          <form onSubmit={handleAdd}>
            <Stack>
              <Title order={5}>Add line item</Title>
              {addError && <Alert color="red">{addError}</Alert>}
              <Select
                label="Category"
                placeholder="Pick a category"
                data={categories.map((c) => ({
                  value: String(c.id),
                  label: `${c.name} (${c.kind})`,
                }))}
                value={addCategoryId}
                onChange={setAddCategoryId}
                required
              />
              <NumberInput
                label="Planned amount"
                value={addAmount}
                onChange={(v) => setAddAmount(String(v))}
                min={0}
                decimalScale={2}
                fixedDecimalScale
                required
              />
              <Group justify="flex-end">
                <Button type="submit">Add item</Button>
              </Group>
            </Stack>
          </form>
        </>
      )}
    </Stack>
  );
}
