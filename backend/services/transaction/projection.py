"""Event consumers that maintain transaction-service's local read-models.

`budget.*` and `category.*` events keep the `budget_projection` /
`category_projection` tables in sync. Handlers are idempotent — an event
delivered more than once leaves the same state — and `deleted` events also
cascade-delete the affected transactions.
"""
from datetime import date

from sqlalchemy import delete as sa_delete
from sqlalchemy.orm import Session

from backend.common.schemas import CategoryKind

from .models import BudgetProjection, CategoryProjection, Transaction


def apply_event(db: Session, event: str, data: dict) -> None:
    """Dispatch a `budget.*` / `category.*` event to the right consumer."""
    if event.startswith("budget."):
        _apply_budget_event(db, event, data)
    elif event.startswith("category."):
        _apply_category_event(db, event, data)


def _apply_budget_event(db: Session, event: str, data: dict) -> None:
    if event in ("budget.created", "budget.updated"):
        # merge() is an idempotent upsert keyed on the primary key.
        db.merge(
            BudgetProjection(
                id=data["id"],
                name=data["name"],
                start_date=date.fromisoformat(data["start_date"]),
                end_date=date.fromisoformat(data["end_date"]),
            )
        )
        db.commit()
    elif event == "budget.deleted":
        budget_id = data["id"]
        # Cascade: drop the budget's transactions, then the projection row.
        db.execute(
            sa_delete(Transaction).where(Transaction.budget_id == budget_id)
        )
        projected = db.get(BudgetProjection, budget_id)
        if projected is not None:
            db.delete(projected)
        db.commit()


def _apply_category_event(db: Session, event: str, data: dict) -> None:
    if event == "category.created":
        db.merge(
            CategoryProjection(
                id=data["id"],
                name=data["name"],
                kind=CategoryKind(data["kind"]),
            )
        )
        db.commit()
    elif event == "category.deleted":
        category_id = data["id"]
        # Cascade: drop transactions classified by the category, then the row.
        db.execute(
            sa_delete(Transaction).where(
                Transaction.category_id == category_id
            )
        )
        projected = db.get(CategoryProjection, category_id)
        if projected is not None:
            db.delete(projected)
        db.commit()
