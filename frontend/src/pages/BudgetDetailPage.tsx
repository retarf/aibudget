import {
  Alert,
  Anchor,
  Button,
  Group,
  Modal,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { useState } from "react";
import { Link, useParams } from "react-router";

import { ApiError, api } from "../api/client";
import type { Transaction, TransactionInput } from "../api/types";
import { TransactionForm } from "../components/TransactionForm";
import { useApiResource } from "../hooks/useApiResource";

export function BudgetDetailPage() {
  const { budgetId } = useParams();
  const id = Number(budgetId);

  const budget = useApiResource(() => api.getBudget(id), [id]);
  const transactions = useApiResource(() => api.listTransactions(id), [id]);
  const categories = useApiResource(() => api.listCategories(), []);

  const [editing, setEditing] = useState<Transaction | "new" | null>(null);
  const [formError, setFormError] = useState<string>();
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState<Transaction | null>(null);

  function categoryName(categoryId: number): string {
    return (
      categories.data?.find((c) => c.id === categoryId)?.name ??
      `#${categoryId}`
    );
  }

  async function handleSubmit(data: TransactionInput) {
    setSubmitting(true);
    setFormError(undefined);
    try {
      if (editing === "new") {
        await api.createTransaction(id, data);
      } else if (editing) {
        await api.updateTransaction(editing.id, data);
      }
      setEditing(null);
      transactions.reload();
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
    await api.deleteTransaction(deleting.id);
    setDeleting(null);
    transactions.reload();
  }

  return (
    <Stack>
      <Anchor component={Link} to="/budgets">
        ← Back to budgets
      </Anchor>

      <Group justify="space-between">
        <Title order={2}>{budget.data?.name ?? "Budget"}</Title>
        <Button
          disabled={!categories.data}
          onClick={() => {
            setFormError(undefined);
            setEditing("new");
          }}
        >
          Record transaction
        </Button>
      </Group>

      {budget.data && (
        <Text c="dimmed">
          {budget.data.start_date} → {budget.data.end_date}
        </Text>
      )}

      {(budget.error || transactions.error) && (
        <Alert color="red">{budget.error ?? transactions.error}</Alert>
      )}
      {!transactions.loading && transactions.data?.length === 0 && (
        <Text c="dimmed">No transactions yet.</Text>
      )}

      {transactions.data && transactions.data.length > 0 && (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Date</Table.Th>
              <Table.Th>Type</Table.Th>
              <Table.Th>Category</Table.Th>
              <Table.Th>Amount</Table.Th>
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {transactions.data.map((transaction) => (
              <Table.Tr key={transaction.id}>
                <Table.Td>{transaction.date}</Table.Td>
                <Table.Td>{transaction.type}</Table.Td>
                <Table.Td>{categoryName(transaction.category_id)}</Table.Td>
                <Table.Td>{transaction.amount}</Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    <Button
                      variant="subtle"
                      size="xs"
                      onClick={() => {
                        setFormError(undefined);
                        setEditing(transaction);
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="subtle"
                      color="red"
                      size="xs"
                      onClick={() => setDeleting(transaction)}
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
        title={editing === "new" ? "Record transaction" : "Edit transaction"}
      >
        <TransactionForm
          categories={categories.data ?? []}
          initial={editing && editing !== "new" ? editing : undefined}
          error={formError}
          submitting={submitting}
          onSubmit={handleSubmit}
        />
      </Modal>

      <Modal
        opened={deleting !== null}
        onClose={() => setDeleting(null)}
        title="Delete transaction"
      >
        <Text>Delete this transaction?</Text>
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
