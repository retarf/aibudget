import { Route, Routes } from "react-router";

import { AppLayout } from "./components/AppLayout";
import { BudgetsPage } from "./pages/BudgetsPage";
import { CategoriesPage } from "./pages/CategoriesPage";
import { DashboardPage } from "./pages/DashboardPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ReportsPage } from "./pages/ReportsPage";

/** Application routes, all rendered inside the shell layout. */
export function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="budgets" element={<BudgetsPage />} />
        <Route path="categories" element={<CategoriesPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
