import {
  Alert,
  Button,
  Group,
  Modal,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { ApiError, api } from "../api/client";
import type { Budget, BudgetInput, BudgetSummary } from "../api/types";
import { BudgetForm } from "../components/BudgetForm";
import { useApiResource } from "../hooks/useApiResource";

export function BudgetsPage() {
  const navigate = useNavigate();
  const budgets = useApiResource(() => api.listBudgets(), []);
  const [summaries, setSummaries] = useState<Record<number, BudgetSummary>>({});
  const [summariesError, setSummariesError] = useState<string>();

  const [editing, setEditing] = useState<Budget | "new" | null>(null);
  const [formError, setFormError] = useState<string>();
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState<Budget | null>(null);

  useEffect(() => {
    if (!budgets.data) return;
    let cancelled = false;
    setSummariesError(undefined);
    Promise.all(
      budgets.data.map((b) =>
        api.getBudgetSummary(b.id).then((s) => [b.id, s] as const),
      ),
    )
      .then((entries) => {
        if (cancelled) return;
        setSummaries(Object.fromEntries(entries));
      })
      .catch((err) => {
        if (cancelled) return;
        setSummariesError(
          err instanceof ApiError ? err.message : "Unexpected error",
        );
        setSummaries({});
      });
    return () => {
      cancelled = true;
    };
  }, [budgets.data]);

  async function handleSubmit(data: BudgetInput, templateId?: number) {
    setSubmitting(true);
    setFormError(undefined);
    try {
      if (editing === "new") {
        const created = await api.createBudget(data);
        if (templateId !== undefined) {
          await api.applyTemplate(created.id, templateId);
        }
      } else if (editing) {
        await api.updateBudget(editing.id, data);
      }
      setEditing(null);
      budgets.reload();
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
    await api.deleteBudget(deleting.id);
    setDeleting(null);
    budgets.reload();
  }

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Budgets</Title>
        <Button
          onClick={() => {
            setFormError(undefined);
            setEditing("new");
          }}
        >
          New budget
        </Button>
      </Group>

      {budgets.error && <Alert color="red">{budgets.error}</Alert>}
      {summariesError && <Alert color="red">{summariesError}</Alert>}
      {!budgets.loading && budgets.data?.length === 0 && (
        <Text c="dimmed">No budgets yet. Create your first one.</Text>
      )}

      {budgets.data && budgets.data.length > 0 && (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Start date</Table.Th>
              <Table.Th>End date</Table.Th>
              <Table.Th>Planned income</Table.Th>
              <Table.Th>Actual income</Table.Th>
              <Table.Th>Planned expense</Table.Th>
              <Table.Th>Actual expense</Table.Th>
              <Table.Th>Net</Table.Th>
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {budgets.data.map((budget) => (
              <Table.Tr key={budget.id}>
                <Table.Td>{budget.name}</Table.Td>
                <Table.Td>{budget.start_date}</Table.Td>
                <Table.Td>{budget.end_date}</Table.Td>
                <Table.Td>
                  {summaries[budget.id]?.totals.planned_income ?? "—"}
                </Table.Td>
                <Table.Td>
                  {summaries[budget.id]?.totals.actual_income ?? "—"}
                </Table.Td>
                <Table.Td>
                  {summaries[budget.id]?.totals.planned_expense ?? "—"}
                </Table.Td>
                <Table.Td>
                  {summaries[budget.id]?.totals.actual_expense ?? "—"}
                </Table.Td>
                <Table.Td>{summaries[budget.id]?.totals.net ?? "—"}</Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    <Button
                      variant="subtle"
                      size="xs"
                      onClick={() => navigate(`/budgets/${budget.id}`)}
                    >
                      Open
                    </Button>
                    <Button
                      variant="subtle"
                      size="xs"
                      onClick={() => {
                        setFormError(undefined);
                        setEditing(budget);
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="subtle"
                      color="red"
                      size="xs"
                      onClick={() => setDeleting(budget)}
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
        opened={editing !== null}
        onClose={() => setEditing(null)}
        title={editing === "new" ? "New budget" : "Edit budget"}
      >
        <BudgetForm
          initial={editing && editing !== "new" ? editing : undefined}
          error={formError}
          submitting={submitting}
          onSubmit={handleSubmit}
        />
      </Modal>

      <Modal
        opened={deleting !== null}
        onClose={() => setDeleting(null)}
        title="Delete budget"
      >
        <Text>
          Delete budget “{deleting?.name}”? This also removes its transactions.
        </Text>
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
