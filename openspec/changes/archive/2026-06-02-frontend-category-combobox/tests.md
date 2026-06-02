# Manual Smoke Test Plan — Category Combobox

## Setup
- [ ] `cli compose up -d`
- [ ] Open the frontend at `http://localhost:${FRONTEND_PORT}` (default `http://localhost:5173`); gateway at `http://localhost:${BACKEND_PORT}` (default `http://localhost:8000`)
- [ ] Through the **Categories** page, ensure these exist: income "Salary"; expense "Food", "Rent"
- [ ] Create a budget (e.g. "May", 2026-05-01 → 2026-05-31) and open its detail page

---

## 1. Categories page and nav are unchanged (regression)
- [ ] **Categories** is still in the left nav and opens the existing page
- [ ] Create / filter-by-kind / delete still work there (this change does not touch it)

---

## Transaction form — the category picker

## 2. Picker is gated until a Type is chosen
- [ ] Click **Record transaction**
- [ ] **Type** shows neither Income nor Expense selected
- [ ] **Category** is disabled with placeholder "Choose a kind first"
- [ ] **Save** is disabled

## 3. Choosing a Type unlocks the picker, filtered to that kind
- [ ] Choose **Expense**; the Category field becomes enabled
- [ ] Opening the list shows only expense categories ("Food", "Rent") — "Salary" is not offered
- [ ] Switch Type to **Income**; the list now shows only "Salary"

## 4. Type to filter
- [ ] With Type = Expense, type `Re`; the list narrows to "Rent" and "Food" disappears

## 5. Tab accepts the best match
- [ ] Type `Foo`, press **Tab**; "Food" is selected and focus moves on
- [ ] No new category is created

## 6. Tab with no match just leaves the field
- [ ] Type `Zzz` (matches nothing), press **Tab**; focus leaves, nothing selected
- [ ] No category named "Zzz" is created

## 7. Enter selects an exact match — never a duplicate
- [ ] Type `Food` exactly, press **Enter**; existing "Food" is selected
- [ ] Categories page still shows only one "Food" expense category

## 8. Enter creates when nothing matches, inheriting the kind
- [ ] With Type = Expense, type `Transport`, press **Enter**; it is created and selected
- [ ] On the Categories page, "Transport" exists with kind **expense**

## 9. The ＋ Create row works with the mouse
- [ ] New transaction, Type = Income, type `Bonus`
- [ ] A "＋ Create "Bonus"" row appears at the bottom of the dropdown
- [ ] Clicking it creates "Bonus" (kind **income**) and selects it

## 10. Changing the Type clears a now-invalid selection
- [ ] New transaction, Type = Expense, select "Food"
- [ ] Switch Type to **Income**; the Category field clears and lists income categories only

## 11. Cannot save until both Type and Category are set
- [ ] Set amount and date but leave Type unset → Save disabled
- [ ] Choose a Type but leave Category empty → Save still disabled
- [ ] Pick a category → Save enables

## 12. Record a transaction end-to-end
- [ ] Type = Expense, amount `30.00`, date in period, category "Food", **Save**
- [ ] Transaction appears in the list; summary actual expense / Net update

## 13. The old inline creator is gone
- [ ] No "+ New category" button or separate name+kind mini-form below the Category field

## 14. Editing a legacy mismatched transaction re-categorizes it
> Only if you have (or create via API, step 18/20) a transaction whose category kind disagrees with its type.
- [ ] Open such a transaction for editing
- [ ] The Category field is empty, forcing a valid re-pick before saving

---

## Allocation panel — the category picker

## 15. Allocation picker is gated by the income/expense toggle
- [ ] In **Planned allocations**, click **Add allocation**
- [ ] An **Income / Expense** toggle shows with neither selected; **Category** is disabled; **Add** is disabled
- [ ] Choose **Expense**; the Category field unlocks and lists expense categories only

## 16. Allocation inline create inherits the toggle kind
- [ ] With the toggle on **Income**, type `Freelance`, press **Enter** (or use ＋ Create)
- [ ] "Freelance" is created with kind **income** and selected

## 17. Add an allocation end-to-end
- [ ] Toggle = Expense, category "Rent", planned amount `500.00`, **Add**
- [ ] The allocation row appears; summary planned-expense updates

## 18. Cannot add until kind + category + amount are set
- [ ] With the toggle unset, **Add** is disabled
- [ ] Add only enables once a kind, a category, and an amount are all provided

---

## Backend enforcement (the invariant is not UI-only)

## 19. API rejects a mismatched category on create
- [ ] Gather ids: `curl -s http://localhost:8000/categories | jq` and `curl -s http://localhost:8000/budgets | jq`
- [ ] Pick budget `B`, **income** category `I`, in-period date `D`; post an expense referencing it:
  ```
  curl -i -X POST http://localhost:8000/budgets/B/transactions \
    -H 'Content-Type: application/json' \
    -d '{"type":"expense","amount":"10.00","date":"D","category_id":I}'
  ```
- [ ] Response is `422` (category kind does not match the transaction type)
- [ ] `GET /budgets/B/transactions` shows nothing was created

## 20. API rejects a mismatched category on update
- [ ] Create a valid expense transaction (expense category), note its id `T`
- [ ] Update it to the income category while keeping `type=expense`:
  ```
  curl -i -X PUT http://localhost:8000/transactions/T \
    -H 'Content-Type: application/json' \
    -d '{"type":"expense","amount":"10.00","date":"D","category_id":I}'
  ```
- [ ] Response is `422`; `GET /transactions/T` shows the original is unchanged

## 21. Matching kind still succeeds
- [ ] Repeat step 19 with an **expense** category under `type=expense`
- [ ] Response is `201` and the transaction is created

---

## Cross-cutting

## 22. Duplicate category name is reported inline
- [ ] In the transaction picker (Type = Expense), type `Food` + **Enter** → existing "Food" selected (no duplicate)
- [ ] If a create is forced for an already-existing name+kind via another path, the API `409` ("already exists for this kind") surfaces inline in the picker

## 23. Summary reconciles after picker-driven edits
- [ ] After recording transactions and adding allocations via the new picker, the per-category planned vs actual reconciles and `Net = actual_income − actual_expense`

---

## Category deletion guard & Erase History

## 24. Unused category shows Delete and deletes
- [ ] On the Categories page, create a fresh category referenced by nothing
- [ ] Its row offers **Delete** and **not** Erase history
- [ ] Delete it → it disappears from the list (`204`)

## 25. In-use category shows Erase history, not Delete
- [ ] Ensure a category (e.g. "Food") is referenced by a transaction, an allocation, and/or a template line item
- [ ] Its row offers **Erase history** and **not** Delete

## 26. Blocked delete returns 409 with counts (API)
- [ ] With "Food" id `C`:
  ```
  curl -i -X DELETE http://localhost:8000/categories/C
  ```
- [ ] Response is `409` and includes counts of referencing transactions, allocations, and templates
- [ ] `GET /categories` shows "Food" still present and unchanged

## 27. Erase history confirmation shows the blast radius
- [ ] Click **Erase history** on "Food"
- [ ] The confirmation shows how many transactions, allocations, and templates will be affected

## 28. Erase history clears the footprint everywhere
- [ ] Confirm the erase
- [ ] **Expect:** "Food" transactions are gone from every budget (past, current, future); its allocations are gone; it's removed from all templates; the category itself still exists
- [ ] The "Food" row now offers **Delete**

## 29. Delete after erase succeeds
- [ ] Click **Delete** on the now-unused "Food", confirm
- [ ] **Expect:** `204`, the category disappears

## 30. Category list reports usage (API)
- [ ] `curl -s http://localhost:8000/categories | jq`
- [ ] **Expect:** each category carries an in-use indicator and usage counts (transactions / allocations / templates)

## 31. Erase history is idempotent / re-runnable
- [ ] Invoke erase-history for a category twice (e.g. re-run the API call)
- [ ] **Expect:** the second call succeeds with nothing left to erase (no error)

## 32. Cascade safety net (optional, race)
- [ ] Not normally observable; if a transaction is somehow created for a category between the gateway's usage check and the delete, the `category.deleted` cascade removes it so no transaction points at a missing category
- [ ] Sanity check: after any category delete, no transaction in any budget references a non-existent category id

---

## Red flags to watch for
- [ ] A wrong-kind category appearing in the picker, or being selectable
- [ ] The Category field usable before a Type / toggle is chosen
- [ ] Typing an existing name + Enter creating a duplicate category
- [ ] A created category getting the wrong kind (not matching the active Type/toggle)
- [ ] Switching Type leaving a stale, mismatched category selected
- [ ] The API accepting a mismatched transaction (any `2xx` in steps 19–20)
- [ ] A leftover "+ New category" button or the old inline mini-form
- [ ] A **Delete** button shown for an in-use category, or a `2xx` from deleting one
- [ ] Both Delete and Erase history shown on the same row at once
- [ ] Erase history leaving any transaction, allocation, or template item behind, or deleting the category itself
- [ ] An orphaned transaction/allocation/template item pointing at a deleted category
