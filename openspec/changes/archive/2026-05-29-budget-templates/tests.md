# Manual Smoke Test Plan — Budget Templates

## Setup
```
cli compose up -d
```
Open `http://localhost:5173`.

Create at least one income category and one expense category through the
**Categories** page (e.g. "Salary" / income, "Food" and "Rent" / expense)
so later steps have categories to reference.

---

## 1. Templates entry is visible in the navigation
1. Open the app.
2. **Expect:** the left navigation lists Dashboard, Budgets, Categories,
   **Templates**, Reports — in that order.

## 2. Templates page empty state
1. Click **Templates**.
2. **Expect:** the page renders with the heading "Templates" and the message
   "No templates yet. Create your first one."

## 3. Create a template
1. Click **New template**.
2. Enter the name "Monthly", click **Create**.
3. **Expect:** the modal closes; "Monthly" appears in the templates list.

## 4. Empty-name guard
1. Click **New template**.
2. Leave the name blank and try to **Create**.
3. **Expect:** the form refuses to submit and the modal stays open.

## 5. Open a template's detail
1. Click **Open** (or the template name link) on the "Monthly" row.
2. **Expect:** a modal opens titled "Template details", shows the template's
   name as a heading, and reads "No line items yet."

## 6. Add a line item
1. In the template-detail modal, pick a category in the **Category** select,
   enter a planned amount (e.g. `500.00`), click **Add item**.
2. **Expect:** the line item appears in the items table with the category
   name and `500.00`.

## 7. Duplicate-category guard
1. Try adding another line item for the **same category** with a different
   amount.
2. **Expect:** an inline error "Category already in template" is shown and the
   table is unchanged.

## 8. Add a second line item with a different category
1. Add an item for a different category, amount `1500.00`.
2. **Expect:** both rows are listed.

## 9. Remove a line item
1. Click **Remove** on one of the rows.
2. **Expect:** the row disappears; the remaining items are unaffected.

## 10. Template selector is hidden when no templates exist
1. Delete the template from the templates list (use **Delete** then confirm).
2. Go to **Budgets** → **New budget**.
3. **Expect:** the form shows Name / Start / End only — no "Start from a
   template" field. Cancel.

## 11. Create a template again (used by remaining steps)
Repeat steps 3, 6, and 8 to recreate "Monthly" with at least two items
(e.g. one expense category at `500.00`, one income category at `1500.00`).

## 12. Create a budget from a template
1. **Budgets** → **New budget**.
2. **Expect:** the "Start from a template" Select is now visible and lists
   "Monthly".
3. Fill name + dates, pick "Monthly", **Save**.
4. **Expect:** new budget row appears with **Planned income** /
   **Planned expense** matching the template totals; **Actual** columns are
   `0.00`; **Net** is `0.00`.

## 13. Create a budget without a template
1. New budget, leave the Select blank.
2. **Expect:** row added with all five totals `0.00`.

## 14. Budget detail — planned-vs-actual block
1. Open the templated budget.
2. **Expect:** five totals shown (Planned/Actual income, Planned/Actual
   expense, Net) plus a per-category table with planned amounts and `0.00`
   actuals.

## 15. Record a transaction and see actuals move
1. From the detail page, **Record transaction**, pick a category that has a
   planned allocation, amount e.g. `120.50`, save.
2. **Expect:**
   - Per-category table updates: planned unchanged, actual = `120.50`.
   - Aggregate totals: matching planned/actual moves; **Net** recomputes as
     `actual_income − actual_expense`.

## 16. Transaction in a category with no allocation
1. Record a transaction for a category that has no allocation.
2. **Expect:** that category appears in the breakdown with
   **Planned = 0.00**, **Actual = recorded amount**.

## 17. Allocation panel — add
1. On the detail page, in **Planned allocations**, click **Add allocation**.
2. Pick a category that isn't yet allocated, enter `300.00`, **Add**.
3. **Expect:** row appears; summary totals update; per-category table now
   shows the new row with `0.00` actual.

## 18. Allocation panel — edit
1. Click the edit (✎) icon on an allocation, change the amount, **Save**.
2. **Expect:** value updates; planned totals reflect the change.

## 19. Allocation panel — delete
1. Click the delete (×) icon.
2. **Expect:** row removed; planned totals drop.

## 20. Duplicate-allocation guard
1. Try to add an allocation for a category that already has one.
2. **Expect:** inline error "Allocation already exists for this category".

## 21. Apply template from the allocation panel
1. On a budget with at least one existing allocation that overlaps the
   "Monthly" template, click **Apply template**, pick "Monthly", **Apply**.
2. **Expect (merge semantics):**
   - The pre-existing overlapping allocation is **unchanged** (template value
     is skipped).
   - Non-overlapping template items are added as new allocations.
   - Summary totals and per-category table update.

## 22. Apply template to an empty budget
1. Create a fresh budget without a template; on the detail page apply
   "Monthly".
2. **Expect:** all template items become allocations 1:1.

## 23. Category-deletion cascade (template items)
1. In **Categories**, delete a category that:
   - Is in the "Monthly" template, AND
   - Has **no transactions** anywhere (category-service rejects the delete
     otherwise).
2. **Expect:** deletion succeeds.
3. Re-open the "Monthly" template from the Templates page.
4. **Expect:** the line item referencing the deleted category is gone; other
   items are intact.

## 24. Allocations are not cascade-deleted by category deletion
1. Apply the template to a budget so a category is referenced both by an
   allocation and a template item.
2. Try deleting that category from the Categories page.
3. The design specifies that allocations are **not** cascaded; the allocation
   referencing the now-deleted category should remain (it records a
   historical planned amount). If the Categories page refuses to delete
   because of allocations, that's a divergence from the design — note it.

## 25. Budget deletion cascades allocations
1. Delete a budget that has allocations.
2. **Expect:** the row disappears from the list; the allocation rows for that
   budget no longer exist server-side.

## 26. Delete a template
1. From the Templates page, click **Delete** on "Monthly", confirm.
2. **Expect:** the row disappears; the template no longer appears in the
   budget creation form's selector or the allocation panel's apply-template
   modal.
3. Existing budgets that were created from "Monthly" keep their allocations
   unchanged (templates and budgets are decoupled after apply).

## 27. Summary for an unknown budget
```
curl -i http://localhost:8000/budgets/999999/summary
```
**Expect:** `404 Budget not found`.

## 28. Two parallel NATS calls under the hood
Tail the gateway logs while loading a budget detail page:
```
docker compose logs -f gateway
```
**Expect:** for each summary request you see two outbound calls
(`budget.allocation.list` + `transaction.summary.categories`) issued
back-to-back, not serial round-trips.

## 29. Decimal formatting
1. Record a transaction with amount `12.5` (no trailing zero typed).
2. **Expect:** the UI and the summary JSON show `"12.50"` (two decimals)
   everywhere.

## 30. Budgets list totals
1. With several budgets, confirm the budgets list shows 5 numeric columns per
   row and that they match each budget's detail page totals.
2. Delete a budget; remaining rows keep their totals.

## 31. Frontend graceful degradation when budget-service is down
1. Stop budget-service: `docker compose stop budget-service`.
2. Open **New budget**.
3. **Expect:** form still renders; the template Select isn't shown
   (template fetch failed silently, by design).
4. Open the **Templates** page.
5. **Expect:** the list shows the surfaced API error (not a crash).
6. Restart: `docker compose start budget-service`.

---

## Red flags to watch for
- Any `500` in the gateway logs when handling `/budgets/.../summary`.
- A planned vs actual that doesn't reconcile to `Net = actual_income − actual_expense`.
- A template `apply` that overwrites an existing allocation (merge should preserve it).
- An allocation row sticking around after its parent budget is deleted.
- A template Select that appears in the budget form when no templates exist.
