# Domain Glossary

## Budget
A named period of time (start_date, end_date) within which a user records transactions. A budget may have zero or more planned allocations.

## Category
A global, workspace-wide label for a type of income or expense (e.g. "Groceries", "Salary"). Categories are shared across all budgets and are not scoped to any single budget or template.

## Transaction
A recorded financial fact — an income or expense — belonging to a specific budget and referencing a specific category. Transactions represent things that actually happened.

## Planned Allocation
A (budget, category, planned_amount) association expressing how much a user intends to spend or earn in a given category for a given budget. Planned allocations are distinct from transactions: they represent intent, not actuals. A budget may have allocations with no corresponding transactions (shown as actual €0) or transactions with no allocation. Allocations are managed either ad-hoc on a budget or by applying a Budget Template.

## Budget Template
A named, reusable entity containing a set of Template Line Items. Applying a template to a budget creates a one-time copy of its line items as planned allocations on that budget; subsequent changes to the template do not affect budgets already created from it. A template can be applied at budget creation time or to an existing budget at any later point.

## Template Line Item
A (category, planned_amount) pair belonging to a Budget Template. Each category may appear at most once per template. When the referenced category is deleted, the line item is cascade-deleted from the template.

## Budget Summary
An aggregate view of a budget showing planned vs actual figures. Includes both aggregate totals (planned income, actual income, planned expense, actual expense, net) and a per-category breakdown. Categories with a planned allocation but no transactions are shown with actual €0. Categories with transactions but no allocation are shown with planned €0.
