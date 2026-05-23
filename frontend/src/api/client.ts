/** Typed REST API client. Every backend endpoint is wrapped here. */
import type {
  Budget,
  BudgetInput,
  BudgetSummary,
  Category,
  CategoryCreate,
  CategoryKind,
  Transaction,
  TransactionInput,
} from "./types";

const BASE_URL =
  typeof __API_URL__ !== "undefined" ? __API_URL__ : "http://localhost:8000";

/** Thrown for any non-2xx response; carries the HTTP status and a message. */
export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function detailOf(body: unknown, status: number): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    // FastAPI request-validation errors: detail is an array of { msg }.
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: unknown };
      if (typeof first?.msg === "string") {
        return first.msg;
      }
    }
  }
  return `Request failed (${status})`;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (response.status === 204) {
    return undefined as T;
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(response.status, detailOf(body, response.status));
  }
  return body as T;
}

export const api = {
  // --- Budgets ---
  listBudgets: () => request<Budget[]>("/budgets"),
  getBudget: (id: number) => request<Budget>(`/budgets/${id}`),
  createBudget: (data: BudgetInput) =>
    request<Budget>("/budgets", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateBudget: (id: number, data: BudgetInput) =>
    request<Budget>(`/budgets/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteBudget: (id: number) =>
    request<void>(`/budgets/${id}`, { method: "DELETE" }),
  getBudgetSummary: (id: number) =>
    request<BudgetSummary>(`/budgets/${id}/summary`),

  // --- Transactions ---
  listTransactions: (budgetId: number) =>
    request<Transaction[]>(`/budgets/${budgetId}/transactions`),
  createTransaction: (budgetId: number, data: TransactionInput) =>
    request<Transaction>(`/budgets/${budgetId}/transactions`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateTransaction: (id: number, data: TransactionInput) =>
    request<Transaction>(`/transactions/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteTransaction: (id: number) =>
    request<void>(`/transactions/${id}`, { method: "DELETE" }),

  // --- Categories ---
  listCategories: (kind?: CategoryKind) =>
    request<Category[]>(`/categories${kind ? `?kind=${kind}` : ""}`),
  createCategory: (data: CategoryCreate) =>
    request<Category>("/categories", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteCategory: (id: number) =>
    request<void>(`/categories/${id}`, { method: "DELETE" }),
};
