import { http, HttpResponse } from "msw";

import type {
  Allocation,
  Budget,
  Category,
  Template,
  TemplateItem,
  Transaction,
} from "../api/types";

// Base URL must match the API client's (jest global __API_URL__).
const API = "http://localhost:8000";

interface Store {
  budgets: Budget[];
  transactions: Transaction[];
  categories: Category[];
  templates: Template[];
  templateItems: (TemplateItem & { template_id: number })[];
  allocations: Allocation[];
  seq: number;
}

let store: Store;

/** Reset the in-memory backend. Called between tests. */
export function resetStore(): void {
  store = {
    budgets: [],
    transactions: [],
    categories: [],
    templates: [],
    templateItems: [],
    allocations: [],
    seq: 0,
  };
}

resetStore();

// --- Seed helpers for tests ---

export function seedBudget(data: Omit<Budget, "id">): Budget {
  const budget = { ...data, id: ++store.seq };
  store.budgets.push(budget);
  return budget;
}

export function seedCategory(data: Omit<Category, "id">): Category {
  const category = { ...data, id: ++store.seq };
  store.categories.push(category);
  return category;
}

export function seedTransaction(data: Omit<Transaction, "id">): Transaction {
  const transaction = { ...data, id: ++store.seq };
  store.transactions.push(transaction);
  return transaction;
}

export function seedTemplate(
  name: string,
  items: { category_id: number; planned_amount: string }[] = [],
): Template {
  const template = { id: ++store.seq, name };
  store.templates.push(template);
  for (const item of items) {
    store.templateItems.push({
      id: ++store.seq,
      template_id: template.id,
      category_id: item.category_id,
      planned_amount: item.planned_amount,
    });
  }
  return template;
}

export function seedAllocation(data: Omit<Allocation, "id">): Allocation {
  const allocation = { ...data, id: ++store.seq };
  store.allocations.push(allocation);
  return allocation;
}

// --- Request handlers mirroring the backend's behavior ---

export const handlers = [
  // Budgets
  http.get(`${API}/budgets`, () => HttpResponse.json(store.budgets)),

  http.get(`${API}/budgets/:id`, ({ params }) => {
    const budget = store.budgets.find((b) => b.id === Number(params.id));
    return budget
      ? HttpResponse.json(budget)
      : HttpResponse.json({ detail: "Budget not found" }, { status: 404 });
  }),

  http.post(`${API}/budgets`, async ({ request }) => {
    const body = (await request.json()) as Omit<Budget, "id">;
    if (body.end_date <= body.start_date) {
      return HttpResponse.json(
        { detail: "end_date must be after start_date" },
        { status: 422 },
      );
    }
    const budget = { ...body, id: ++store.seq };
    store.budgets.push(budget);
    return HttpResponse.json(budget, { status: 201 });
  }),

  http.put(`${API}/budgets/:id`, async ({ params, request }) => {
    const budget = store.budgets.find((b) => b.id === Number(params.id));
    if (!budget) {
      return HttpResponse.json({ detail: "Budget not found" }, { status: 404 });
    }
    Object.assign(budget, await request.json());
    return HttpResponse.json(budget);
  }),

  http.delete(`${API}/budgets/:id`, ({ params }) => {
    const id = Number(params.id);
    store.budgets = store.budgets.filter((b) => b.id !== id);
    store.transactions = store.transactions.filter((t) => t.budget_id !== id);
    store.allocations = store.allocations.filter((a) => a.budget_id !== id);
    return new HttpResponse(null, { status: 204 });
  }),

  http.get(`${API}/budgets/:id/summary`, ({ params }) => {
    const id = Number(params.id);
    const budget = store.budgets.find((b) => b.id === id);
    if (!budget) {
      return HttpResponse.json({ detail: "Budget not found" }, { status: 404 });
    }

    const allocationsForBudget = store.allocations.filter(
      (a) => a.budget_id === id,
    );
    const transactionsForBudget = store.transactions.filter(
      (t) => t.budget_id === id,
    );
    const categoriesSeen = new Set<number>();
    const rows: {
      category_id: number;
      kind: "income" | "expense";
      planned_amount: string;
      actual_amount: string;
    }[] = [];

    let plannedIncome = 0;
    let actualIncome = 0;
    let plannedExpense = 0;
    let actualExpense = 0;

    const grouped = new Map<
      string,
      { category_id: number; kind: "income" | "expense"; amount: number }
    >();
    for (const t of transactionsForBudget) {
      const key = `${t.category_id}-${t.type}`;
      const existing = grouped.get(key);
      if (existing) {
        existing.amount += Number(t.amount);
      } else {
        grouped.set(key, {
          category_id: t.category_id,
          kind: t.type,
          amount: Number(t.amount),
        });
      }
    }

    for (const { category_id, kind, amount } of grouped.values()) {
      categoriesSeen.add(category_id);
      const plannedAmount = Number(
        allocationsForBudget.find((a) => a.category_id === category_id)
          ?.planned_amount ?? 0,
      );
      rows.push({
        category_id,
        kind,
        planned_amount: plannedAmount.toFixed(2),
        actual_amount: amount.toFixed(2),
      });
      if (kind === "income") {
        plannedIncome += plannedAmount;
        actualIncome += amount;
      } else {
        plannedExpense += plannedAmount;
        actualExpense += amount;
      }
    }

    for (const a of allocationsForBudget) {
      if (categoriesSeen.has(a.category_id)) continue;
      const planned = Number(a.planned_amount);
      const category = store.categories.find((c) => c.id === a.category_id);
      const kind = category?.kind ?? "expense";
      rows.push({
        category_id: a.category_id,
        kind,
        planned_amount: planned.toFixed(2),
        actual_amount: "0.00",
      });
      if (kind === "income") {
        plannedIncome += planned;
      } else {
        plannedExpense += planned;
      }
    }

    return HttpResponse.json({
      budget_id: id,
      totals: {
        planned_income: plannedIncome.toFixed(2),
        actual_income: actualIncome.toFixed(2),
        planned_expense: plannedExpense.toFixed(2),
        actual_expense: actualExpense.toFixed(2),
        net: (actualIncome - actualExpense).toFixed(2),
      },
      categories: rows,
    });
  }),

  // Transactions
  http.get(`${API}/budgets/:id/transactions`, ({ params }) =>
    HttpResponse.json(
      store.transactions.filter((t) => t.budget_id === Number(params.id)),
    ),
  ),

  http.post(`${API}/budgets/:id/transactions`, async ({ params, request }) => {
    const budget = store.budgets.find((b) => b.id === Number(params.id));
    if (!budget) {
      return HttpResponse.json({ detail: "Budget not found" }, { status: 404 });
    }
    const body = (await request.json()) as Omit<
      Transaction,
      "id" | "budget_id"
    >;
    if (body.date < budget.start_date || body.date > budget.end_date) {
      return HttpResponse.json(
        { detail: "Transaction date is outside the budget period" },
        { status: 422 },
      );
    }
    const transaction = { ...body, budget_id: budget.id, id: ++store.seq };
    store.transactions.push(transaction);
    return HttpResponse.json(transaction, { status: 201 });
  }),

  http.put(`${API}/transactions/:id`, async ({ params, request }) => {
    const transaction = store.transactions.find(
      (t) => t.id === Number(params.id),
    );
    if (!transaction) {
      return HttpResponse.json(
        { detail: "Transaction not found" },
        { status: 404 },
      );
    }
    Object.assign(transaction, await request.json());
    return HttpResponse.json(transaction);
  }),

  http.delete(`${API}/transactions/:id`, ({ params }) => {
    store.transactions = store.transactions.filter(
      (t) => t.id !== Number(params.id),
    );
    return new HttpResponse(null, { status: 204 });
  }),

  // Categories
  http.get(`${API}/categories`, ({ request }) => {
    const kind = new URL(request.url).searchParams.get("kind");
    return HttpResponse.json(
      kind
        ? store.categories.filter((c) => c.kind === kind)
        : store.categories,
    );
  }),

  http.post(`${API}/categories`, async ({ request }) => {
    const body = (await request.json()) as Omit<Category, "id">;
    const duplicate = store.categories.some(
      (c) => c.name === body.name && c.kind === body.kind,
    );
    if (duplicate) {
      return HttpResponse.json(
        { detail: "A category with this name already exists for this kind" },
        { status: 409 },
      );
    }
    const category = { ...body, id: ++store.seq };
    store.categories.push(category);
    return HttpResponse.json(category, { status: 201 });
  }),

  http.delete(`${API}/categories/:id`, ({ params }) => {
    const id = Number(params.id);
    if (store.transactions.some((t) => t.category_id === id)) {
      return HttpResponse.json(
        { detail: "Category is referenced by a transaction" },
        { status: 409 },
      );
    }
    store.categories = store.categories.filter((c) => c.id !== id);
    return new HttpResponse(null, { status: 204 });
  }),

  // Templates
  http.get(`${API}/templates`, () => HttpResponse.json(store.templates)),

  http.get(`${API}/templates/:id`, ({ params }) => {
    const id = Number(params.id);
    const template = store.templates.find((t) => t.id === id);
    if (!template) {
      return HttpResponse.json(
        { detail: "Template not found" },
        { status: 404 },
      );
    }
    const items = store.templateItems
      .filter((item) => item.template_id === id)
      .map(({ id: itemId, category_id, planned_amount }) => ({
        id: itemId,
        category_id,
        planned_amount,
      }));
    return HttpResponse.json({ ...template, items });
  }),

  http.post(`${API}/templates`, async ({ request }) => {
    const body = (await request.json()) as { name: string };
    const template = { id: ++store.seq, name: body.name };
    store.templates.push(template);
    return HttpResponse.json(template, { status: 201 });
  }),

  http.delete(`${API}/templates/:id`, ({ params }) => {
    const id = Number(params.id);
    store.templates = store.templates.filter((t) => t.id !== id);
    store.templateItems = store.templateItems.filter(
      (i) => i.template_id !== id,
    );
    return new HttpResponse(null, { status: 204 });
  }),

  http.post(`${API}/templates/:id/items`, async ({ params, request }) => {
    const templateId = Number(params.id);
    const body = (await request.json()) as {
      category_id: number;
      planned_amount: string;
    };
    if (
      store.templateItems.some(
        (i) =>
          i.template_id === templateId && i.category_id === body.category_id,
      )
    ) {
      return HttpResponse.json(
        { detail: "Category already in template" },
        { status: 409 },
      );
    }
    const item = {
      id: ++store.seq,
      template_id: templateId,
      category_id: body.category_id,
      planned_amount: body.planned_amount,
    };
    store.templateItems.push(item);
    return HttpResponse.json(
      {
        id: item.id,
        category_id: item.category_id,
        planned_amount: item.planned_amount,
      },
      { status: 201 },
    );
  }),

  http.delete(
    `${API}/templates/:templateId/items/:itemId`,
    ({ params }) => {
      const templateId = Number(params.templateId);
      const itemId = Number(params.itemId);
      store.templateItems = store.templateItems.filter(
        (i) => !(i.template_id === templateId && i.id === itemId),
      );
      return new HttpResponse(null, { status: 204 });
    },
  ),

  http.post(
    `${API}/budgets/:id/apply-template`,
    async ({ params, request }) => {
      const budgetId = Number(params.id);
      const budget = store.budgets.find((b) => b.id === budgetId);
      if (!budget) {
        return HttpResponse.json(
          { detail: "Budget not found" },
          { status: 404 },
        );
      }
      const body = (await request.json()) as { template_id: number };
      const items = store.templateItems.filter(
        (i) => i.template_id === body.template_id,
      );
      if (items.length === 0) {
        const template = store.templates.find(
          (t) => t.id === body.template_id,
        );
        if (!template) {
          return HttpResponse.json(
            { detail: "Template not found" },
            { status: 404 },
          );
        }
      }
      const existing = new Set(
        store.allocations
          .filter((a) => a.budget_id === budgetId)
          .map((a) => a.category_id),
      );
      const created: Allocation[] = [];
      for (const item of items) {
        if (existing.has(item.category_id)) continue;
        const allocation = {
          id: ++store.seq,
          budget_id: budgetId,
          category_id: item.category_id,
          planned_amount: item.planned_amount,
        };
        store.allocations.push(allocation);
        created.push(allocation);
      }
      return HttpResponse.json(created);
    },
  ),

  // Allocations
  http.get(`${API}/budgets/:id/allocations`, ({ params }) => {
    const id = Number(params.id);
    if (!store.budgets.some((b) => b.id === id)) {
      return HttpResponse.json(
        { detail: "Budget not found" },
        { status: 404 },
      );
    }
    return HttpResponse.json(
      store.allocations.filter((a) => a.budget_id === id),
    );
  }),

  http.post(`${API}/budgets/:id/allocations`, async ({ params, request }) => {
    const budgetId = Number(params.id);
    if (!store.budgets.some((b) => b.id === budgetId)) {
      return HttpResponse.json(
        { detail: "Budget not found" },
        { status: 404 },
      );
    }
    const body = (await request.json()) as {
      category_id: number;
      planned_amount: string;
    };
    if (
      store.allocations.some(
        (a) =>
          a.budget_id === budgetId && a.category_id === body.category_id,
      )
    ) {
      return HttpResponse.json(
        { detail: "Allocation already exists for this category" },
        { status: 409 },
      );
    }
    const allocation = {
      id: ++store.seq,
      budget_id: budgetId,
      category_id: body.category_id,
      planned_amount: body.planned_amount,
    };
    store.allocations.push(allocation);
    return HttpResponse.json(allocation, { status: 201 });
  }),

  http.put(
    `${API}/budgets/:budgetId/allocations/:allocationId`,
    async ({ params, request }) => {
      const allocation = store.allocations.find(
        (a) =>
          a.budget_id === Number(params.budgetId) &&
          a.id === Number(params.allocationId),
      );
      if (!allocation) {
        return HttpResponse.json(
          { detail: "Allocation not found" },
          { status: 404 },
        );
      }
      const body = (await request.json()) as { planned_amount: string };
      allocation.planned_amount = body.planned_amount;
      return HttpResponse.json(allocation);
    },
  ),

  http.delete(
    `${API}/budgets/:budgetId/allocations/:allocationId`,
    ({ params }) => {
      const budgetId = Number(params.budgetId);
      const allocationId = Number(params.allocationId);
      store.allocations = store.allocations.filter(
        (a) => !(a.budget_id === budgetId && a.id === allocationId),
      );
      return new HttpResponse(null, { status: 204 });
    },
  ),
];
