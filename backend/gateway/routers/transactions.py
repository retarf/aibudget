"""Transaction REST routes — same contract as the monolith, served over NATS.

Transactions are created/listed under a budget, but addressed directly by id
for retrieve/update/delete. The summary route aggregates two NATS calls — the
budget's planned allocations from budget-service and the per-category actual
sums from transaction-service — and merges them into a single response.
"""
import asyncio
from decimal import Decimal

from fastapi import APIRouter, status

from backend.common.schemas import (
    BudgetSummary,
    BudgetSummaryCategory,
    BudgetSummaryTotals,
    CategoryKind,
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)

from ..nats_client import call

router = APIRouter(tags=["transactions"])

_ZERO = Decimal("0.00")


@router.post(
    "/budgets/{budget_id}/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(budget_id: int, data: TransactionCreate):
    return await call(
        "transaction.create",
        {"budget_id": budget_id, **data.model_dump(mode="json")},
    )


@router.get(
    "/budgets/{budget_id}/transactions", response_model=list[TransactionRead]
)
async def list_transactions(budget_id: int):
    return await call("transaction.list", {"budget_id": budget_id})


@router.get("/budgets/{budget_id}/summary", response_model=BudgetSummary)
async def summarize_budget(budget_id: int):
    allocations, actuals = await asyncio.gather(
        call("budget.allocation.list", {"budget_id": budget_id}),
        call(
            "transaction.summary.categories", {"budget_id": budget_id}
        ),
    )
    return _merge_summary(budget_id, allocations, actuals).model_dump(
        mode="json"
    )


def _merge_summary(
    budget_id: int, allocations: list[dict], actuals: list[dict]
) -> BudgetSummary:
    """Combine planned allocations and per-category actuals into a summary."""
    planned_by_category: dict[int, Decimal] = {
        a["category_id"]: Decimal(a["planned_amount"]) for a in allocations
    }
    actuals_by_category: dict[int, dict] = {}
    for row in actuals:
        actuals_by_category[row["category_id"]] = row

    rows: list[BudgetSummaryCategory] = []
    seen: set[int] = set()
    for row in actuals:
        category_id = row["category_id"]
        seen.add(category_id)
        rows.append(
            BudgetSummaryCategory(
                category_id=category_id,
                kind=CategoryKind(row["kind"]),
                planned_amount=planned_by_category.get(category_id, _ZERO),
                actual_amount=_actual_for_kind(row),
            )
        )
    for category_id, planned in planned_by_category.items():
        if category_id in seen:
            continue
        rows.append(
            BudgetSummaryCategory(
                category_id=category_id,
                # No actual transactions to dictate kind; placeholder default.
                kind=CategoryKind.expense,
                planned_amount=planned,
                actual_amount=_ZERO,
            )
        )

    planned_income = _ZERO
    actual_income = _ZERO
    planned_expense = _ZERO
    actual_expense = _ZERO
    for row in rows:
        if row.kind == CategoryKind.income:
            planned_income += row.planned_amount
            actual_income += row.actual_amount
        else:
            planned_expense += row.planned_amount
            actual_expense += row.actual_amount

    totals = BudgetSummaryTotals(
        planned_income=planned_income.quantize(_ZERO),
        actual_income=actual_income.quantize(_ZERO),
        planned_expense=planned_expense.quantize(_ZERO),
        actual_expense=actual_expense.quantize(_ZERO),
        net=(actual_income - actual_expense).quantize(_ZERO),
    )
    return BudgetSummary(budget_id=budget_id, totals=totals, categories=rows)


def _actual_for_kind(row: dict) -> Decimal:
    """Pick the field on a `CategorySummary` row matching its kind."""
    return Decimal(row[row["kind"]])


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
async def get_transaction(transaction_id: int):
    return await call(
        "transaction.get", {"transaction_id": transaction_id}
    )


@router.put("/transactions/{transaction_id}", response_model=TransactionRead)
async def update_transaction(transaction_id: int, data: TransactionUpdate):
    return await call(
        "transaction.update",
        {"transaction_id": transaction_id, **data.model_dump(mode="json")},
    )


@router.delete(
    "/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_transaction(transaction_id: int):
    await call("transaction.delete", {"transaction_id": transaction_id})
