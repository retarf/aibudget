import { http, HttpResponse } from "msw";

import type { Budget, Category, Transaction } from "../api/types";

// Base URL must match the API client's (jest global __API_URL__).
const API = "http://localhost:8000";

interface Store {
  budgets: Budget[];
  transactions: Transaction[];
  categories: Category[];
  seq: number;
}

let store: Store;

/** Reset the in-memory backend. Called between tests. */
export function resetStore(): void {
  store = { budgets: [], transactions: [], categories: [], seq: 0 };
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
    return new HttpResponse(null, { status: 204 });
  }),

  http.get(`${API}/budgets/:id/summary`, ({ params }) => {
    const id = Number(params.id);
    const budget = store.budgets.find((b) => b.id === id);
    if (!budget) {
      return HttpResponse.json({ detail: "Budget not found" }, { status: 404 });
    }
    let income = 0;
    let expense = 0;
    for (const t of store.transactions) {
      if (t.budget_id !== id) continue;
      if (t.type === "income") income += Number(t.amount);
      else expense += Number(t.amount);
    }
    return HttpResponse.json({
      budget_id: id,
      totals: {
        income: income.toFixed(2),
        expense: expense.toFixed(2),
        net: (income - expense).toFixed(2),
      },
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
];
