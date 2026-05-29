"""Request/reply handlers for transaction-service.

Ported from the monolith's ``backend/services/transaction.py``. The key change
is ``_validate``: instead of reading the ``Budget`` and ``Category`` tables
directly, it reads the local ``BudgetProjection`` / ``CategoryProjection``
read-models fed by events (eventually consistent — see design.md).
"""
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.common.health import health_handler
from backend.common.messaging import Outcome, ServiceError
from backend.common.schemas import (
    CategorySummary,
    TransactionCreate,
    TransactionRead,
    TransactionType,
    TransactionUpdate,
)

from .models import BudgetProjection, CategoryProjection, Transaction

_ZERO = Decimal("0.00")


def _read(transaction: Transaction) -> dict:
    """Serialize a transaction to a JSON-able dict for envelopes and events."""
    return TransactionRead.model_validate(transaction).model_dump(mode="json")


def _get_budget(db: Session, budget_id: int) -> BudgetProjection:
    budget = db.get(BudgetProjection, budget_id)
    if budget is None:
        raise ServiceError(404, "Budget not found")
    return budget


def _get_transaction(db: Session, transaction_id: int) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise ServiceError(404, "Transaction not found")
    return transaction


def _validate(
    db: Session,
    budget: BudgetProjection,
    data: TransactionCreate | TransactionUpdate,
) -> None:
    """Domain rules beyond field validation, checked against the projections."""
    if not budget.start_date <= data.date <= budget.end_date:
        raise ServiceError(
            422, "Transaction date is outside the budget period"
        )
    if db.get(CategoryProjection, data.category_id) is None:
        raise ServiceError(422, "Category does not exist")


def create_transaction(db: Session, request: dict) -> Outcome:
    budget = _get_budget(db, request["budget_id"])
    data = TransactionCreate.model_validate(request)
    _validate(db, budget, data)
    transaction = Transaction(
        budget_id=budget.id,
        category_id=data.category_id,
        type=data.type,
        amount=data.amount,
        date=data.date,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    payload = _read(transaction)
    return Outcome(reply=payload, event_change="created", event_data=payload)


def list_transactions(db: Session, request: dict) -> Outcome:
    budget_id = request["budget_id"]
    _get_budget(db, budget_id)  # 404 if the budget is unknown
    transactions = db.scalars(
        select(Transaction).where(Transaction.budget_id == budget_id)
    )
    return Outcome(reply=[_read(t) for t in transactions])


def get_transaction(db: Session, request: dict) -> Outcome:
    return Outcome(reply=_read(_get_transaction(db, request["transaction_id"])))


def update_transaction(db: Session, request: dict) -> Outcome:
    transaction = _get_transaction(db, request["transaction_id"])
    budget = _get_budget(db, transaction.budget_id)
    data = TransactionUpdate.model_validate(request)
    _validate(db, budget, data)
    transaction.type = data.type
    transaction.amount = data.amount
    transaction.date = data.date
    transaction.category_id = data.category_id
    db.commit()
    db.refresh(transaction)
    payload = _read(transaction)
    return Outcome(reply=payload, event_change="updated", event_data=payload)


def delete_transaction(db: Session, request: dict) -> Outcome:
    transaction = _get_transaction(db, request["transaction_id"])
    transaction_id = transaction.id
    db.delete(transaction)
    db.commit()
    return Outcome(
        reply=None, event_change="deleted", event_data={"id": transaction_id}
    )


def summarize_by_category(db: Session, request: dict) -> Outcome:
    """Per-category actual income/expense sums for the gateway summary.

    Returns one row per ``(category_id, kind)`` pair appearing in the budget's
    transactions. ``kind`` matches the transaction type, since a single
    category may legitimately appear under both kinds in this domain.
    """
    budget_id = request["budget_id"]
    _get_budget(db, budget_id)  # 404 if the budget is unknown

    rows = db.execute(
        select(
            Transaction.category_id,
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .where(Transaction.budget_id == budget_id)
        .group_by(Transaction.category_id, Transaction.type)
    ).all()

    summary: dict[tuple[int, TransactionType], dict[str, Decimal]] = {}
    for category_id, tx_type, total in rows:
        key = (category_id, tx_type)
        bucket = summary.setdefault(
            key, {"income": _ZERO, "expense": _ZERO}
        )
        bucket[tx_type.value] = Decimal(total).quantize(_ZERO)

    reply = [
        CategorySummary(
            category_id=category_id,
            kind=tx_type.value,
            income=bucket["income"],
            expense=bucket["expense"],
        ).model_dump(mode="json")
        for (category_id, tx_type), bucket in summary.items()
    ]
    return Outcome(reply=reply)


# Maps the operation name in a `transaction.<operation>` subject to its handler.
HANDLERS = {
    "create": create_transaction,
    "list": list_transactions,
    "get": get_transaction,
    "update": update_transaction,
    "delete": delete_transaction,
    "summary.categories": summarize_by_category,
    "health": health_handler,
}
