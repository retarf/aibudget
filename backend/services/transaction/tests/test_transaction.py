"""Tests for transaction-service: handlers, projection, and cascades."""
from datetime import date

import pytest
from sqlalchemy import select

from backend.common.messaging import ServiceError
from backend.common.schemas import CategoryKind
from backend.services.transaction import handlers, projection
from backend.services.transaction.models import (
    BudgetProjection,
    CategoryProjection,
    Transaction,
)


def _seed_budget(db, budget_id=1, start="2026-05-01", end="2026-05-31"):
    db.add(
        BudgetProjection(
            id=budget_id,
            name="May",
            start_date=date.fromisoformat(start),
            end_date=date.fromisoformat(end),
        )
    )
    db.commit()


def _seed_category(db, category_id=1):
    db.add(
        CategoryProjection(
            id=category_id, name="Rent", kind=CategoryKind.expense
        )
    )
    db.commit()


def _create(db, **overrides):
    request = {
        "budget_id": 1,
        "type": "expense",
        "amount": "10.00",
        "date": "2026-05-10",
        "category_id": 1,
    }
    request.update(overrides)
    return handlers.create_transaction(db, request)


# --- handler validation against the projection ------------------------------

def test_create_with_valid_references_succeeds(db):
    _seed_budget(db)
    _seed_category(db)
    outcome = _create(db)
    assert outcome.reply["budget_id"] == 1
    assert outcome.event_change == "created"


def test_create_with_unknown_budget_raises_404(db):
    _seed_category(db)
    with pytest.raises(ServiceError) as exc:
        _create(db)
    assert exc.value.status == 404


def test_create_with_unknown_category_raises_422(db):
    _seed_budget(db)
    with pytest.raises(ServiceError) as exc:
        _create(db)
    assert exc.value.status == 422


def test_create_with_date_outside_period_raises_422(db):
    _seed_budget(db)
    _seed_category(db)
    with pytest.raises(ServiceError) as exc:
        _create(db, date="2026-07-01")
    assert exc.value.status == 422


def test_list_get_update_delete(db):
    _seed_budget(db)
    _seed_category(db)
    transaction_id = _create(db).reply["id"]

    listed = handlers.list_transactions(db, {"budget_id": 1})
    assert len(listed.reply) == 1

    fetched = handlers.get_transaction(db, {"transaction_id": transaction_id})
    assert fetched.reply["id"] == transaction_id

    updated = handlers.update_transaction(
        db,
        {
            "transaction_id": transaction_id,
            "type": "expense",
            "amount": "25.00",
            "date": "2026-05-15",
            "category_id": 1,
        },
    )
    assert updated.reply["amount"] == "25.00"
    assert updated.event_change == "updated"

    deleted = handlers.delete_transaction(
        db, {"transaction_id": transaction_id}
    )
    assert deleted.event_change == "deleted"
    with pytest.raises(ServiceError):
        handlers.get_transaction(db, {"transaction_id": transaction_id})


# --- projection consumers ---------------------------------------------------

def test_budget_event_updates_projection(db):
    projection.apply_event(
        db,
        "budget.created",
        {
            "id": 7,
            "name": "July",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
    )
    assert db.get(BudgetProjection, 7) is not None


def test_budget_event_is_idempotent(db):
    event = {
        "id": 7,
        "name": "July",
        "start_date": "2026-07-01",
        "end_date": "2026-07-31",
    }
    projection.apply_event(db, "budget.created", event)
    projection.apply_event(db, "budget.created", event)
    assert len(list(db.scalars(select(BudgetProjection)))) == 1


def test_budget_deleted_cascades_transactions(db):
    _seed_budget(db)
    _seed_category(db)
    _create(db)
    projection.apply_event(db, "budget.deleted", {"id": 1})
    assert list(db.scalars(select(Transaction))) == []
    assert db.get(BudgetProjection, 1) is None


def test_category_deleted_cascades_transactions(db):
    _seed_budget(db)
    _seed_category(db)
    _create(db)
    projection.apply_event(db, "category.deleted", {"id": 1})
    assert list(db.scalars(select(Transaction))) == []
    assert db.get(CategoryProjection, 1) is None


# --- summary ----------------------------------------------------------------

def _seed_income_category(db, category_id=2):
    db.add(
        CategoryProjection(
            id=category_id, name="Salary", kind=CategoryKind.income
        )
    )
    db.commit()


def test_summary_categories_for_unknown_budget_raises_404(db):
    with pytest.raises(ServiceError) as exc:
        handlers.summarize_by_category(db, {"budget_id": 999})
    assert exc.value.status == 404


def test_summary_categories_for_budget_without_transactions_returns_empty(db):
    _seed_budget(db)
    outcome = handlers.summarize_by_category(db, {"budget_id": 1})
    assert outcome.reply == []
    assert outcome.event_change is None


def test_summary_categories_groups_by_category_and_kind(db):
    _seed_budget(db)
    _seed_category(db)
    _seed_income_category(db)
    _create(db, type="expense", amount="45.50", category_id=1)
    _create(db, type="expense", amount="4.50", category_id=1)
    _create(db, type="income", amount="120.00", category_id=2)
    outcome = handlers.summarize_by_category(db, {"budget_id": 1})
    by_key = {(row["category_id"], row["kind"]): row for row in outcome.reply}
    assert by_key[(1, "expense")]["expense"] == "50.00"
    assert by_key[(1, "expense")]["income"] == "0.00"
    assert by_key[(2, "income")]["income"] == "120.00"
    assert by_key[(2, "income")]["expense"] == "0.00"


def test_summary_categories_decimal_precision(db):
    _seed_budget(db)
    _seed_category(db)
    _create(db, type="expense", amount="12.50", category_id=1)
    _create(db, type="expense", amount="7.50", category_id=1)
    outcome = handlers.summarize_by_category(db, {"budget_id": 1})
    assert outcome.reply[0]["expense"] == "20.00"
