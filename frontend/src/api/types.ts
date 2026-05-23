/** Domain types mirroring the backend REST API. */

export type CategoryKind = "income" | "expense";
export type TransactionType = "income" | "expense";

export interface Category {
  id: number;
  name: string;
  kind: CategoryKind;
}

export interface CategoryCreate {
  name: string;
  kind: CategoryKind;
}

export interface Budget {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
}

export interface BudgetInput {
  name: string;
  start_date: string;
  end_date: string;
}

export interface Transaction {
  id: number;
  budget_id: number;
  category_id: number;
  type: TransactionType;
  amount: string;
  date: string;
}

export interface TransactionInput {
  type: TransactionType;
  amount: string;
  date: string;
  category_id: number;
}

export interface BudgetSummaryTotals {
  income: string;
  expense: string;
  net: string;
}

export interface BudgetSummary {
  budget_id: number;
  totals: BudgetSummaryTotals;
}
