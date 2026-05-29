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
  planned_income: string;
  actual_income: string;
  planned_expense: string;
  actual_expense: string;
  net: string;
}

export interface BudgetSummaryCategory {
  category_id: number;
  kind: CategoryKind;
  planned_amount: string;
  actual_amount: string;
}

export interface BudgetSummary {
  budget_id: number;
  totals: BudgetSummaryTotals;
  categories: BudgetSummaryCategory[];
}

export interface TemplateItem {
  id: number;
  category_id: number;
  planned_amount: string;
}

export interface Template {
  id: number;
  name: string;
}

export interface TemplateDetail extends Template {
  items: TemplateItem[];
}

export interface TemplateCreate {
  name: string;
}

export interface TemplateItemCreate {
  category_id: number;
  planned_amount: string;
}

export interface ApplyTemplate {
  template_id: number;
}

export interface Allocation {
  id: number;
  budget_id: number;
  category_id: number;
  planned_amount: string;
}

export interface AllocationCreate {
  category_id: number;
  planned_amount: string;
}

export interface AllocationUpdate {
  planned_amount: string;
}
