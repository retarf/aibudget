import { Route, Routes } from "react-router";

import { AppLayout } from "./components/AppLayout";
import { BudgetDetailPage } from "./pages/BudgetDetailPage";
import { BudgetsPage } from "./pages/BudgetsPage";
import { CategoriesPage } from "./pages/CategoriesPage";
import { DashboardPage } from "./pages/DashboardPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ReportsPage } from "./pages/ReportsPage";
import { TemplatesPage } from "./pages/TemplatesPage";

/** Application routes, all rendered inside the shell layout. */
export function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="budgets" element={<BudgetsPage />} />
        <Route path="budgets/:budgetId" element={<BudgetDetailPage />} />
        <Route path="categories" element={<CategoriesPage />} />
        <Route path="templates" element={<TemplatesPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
