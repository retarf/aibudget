"""Request/reply handlers for budget-service.

Each handler is a sync ``fn(db, request) -> Outcome``: it performs the
operation and returns the reply payload plus, for state changes, the domain
event to publish. Ported from the monolith's ``backend/services/budget.py``,
with ``HTTPException`` replaced by ``ServiceError``.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.common.health import health_handler
from backend.common.messaging import Outcome, ServiceError
from backend.common.schemas import BudgetCreate, BudgetRead, BudgetUpdate

from .models import Budget


def _read(budget: Budget) -> dict:
    """Serialize a budget to a JSON-able dict for envelopes and events."""
    return BudgetRead.model_validate(budget).model_dump(mode="json")


def _get(db: Session, budget_id: int) -> Budget:
    budget = db.get(Budget, budget_id)
    if budget is None:
        raise ServiceError(404, "Budget not found")
    return budget


def create_budget(db: Session, request: dict) -> Outcome:
    data = BudgetCreate.model_validate(request)
    budget = Budget(
        name=data.name, start_date=data.start_date, end_date=data.end_date
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    payload = _read(budget)
    return Outcome(reply=payload, event_change="created", event_data=payload)


def list_budgets(db: Session, request: dict) -> Outcome:
    budgets = db.scalars(select(Budget))
    return Outcome(reply=[_read(b) for b in budgets])


def get_budget(db: Session, request: dict) -> Outcome:
    return Outcome(reply=_read(_get(db, request["budget_id"])))


def update_budget(db: Session, request: dict) -> Outcome:
    budget = _get(db, request["budget_id"])
    data = BudgetUpdate.model_validate(request)
    budget.name = data.name
    budget.start_date = data.start_date
    budget.end_date = data.end_date
    db.commit()
    db.refresh(budget)
    payload = _read(budget)
    return Outcome(reply=payload, event_change="updated", event_data=payload)


def delete_budget(db: Session, request: dict) -> Outcome:
    budget = _get(db, request["budget_id"])
    budget_id = budget.id
    db.delete(budget)
    db.commit()
    return Outcome(
        reply=None, event_change="deleted", event_data={"id": budget_id}
    )


# Maps the operation name in a `budget.<operation>` subject to its handler.
HANDLERS = {
    "create": create_budget,
    "list": list_budgets,
    "get": get_budget,
    "update": update_budget,
    "delete": delete_budget,
    "health": health_handler,
}
