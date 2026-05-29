"""Tests for budget-service allocation handlers."""
import pytest

from backend.common.messaging import ServiceError
from backend.services.budget import handlers


def _create_budget(db, name="May", start="2026-05-01", end="2026-05-31"):
    return handlers.create_budget(
        db, {"name": name, "start_date": start, "end_date": end}
    )


def test_create_allocation_returns_allocation(db):
    budget_id = _create_budget(db).reply["id"]
    outcome = handlers.create_allocation(
        db,
        {"budget_id": budget_id, "category_id": 1, "planned_amount": "100.00"},
    )
    assert outcome.reply["budget_id"] == budget_id
    assert outcome.reply["category_id"] == 1
    assert outcome.reply["planned_amount"] == "100.00"


def test_create_duplicate_allocation_returns_409(db):
    budget_id = _create_budget(db).reply["id"]
    handlers.create_allocation(
        db,
        {"budget_id": budget_id, "category_id": 1, "planned_amount": "100.00"},
    )
    with pytest.raises(ServiceError) as exc:
        handlers.create_allocation(
            db,
            {
                "budget_id": budget_id,
                "category_id": 1,
                "planned_amount": "200.00",
            },
        )
    assert exc.value.status == 409


def test_create_allocation_unknown_budget_returns_404(db):
    with pytest.raises(ServiceError) as exc:
        handlers.create_allocation(
            db,
            {"budget_id": 999, "category_id": 1, "planned_amount": "100.00"},
        )
    assert exc.value.status == 404


def test_list_allocations_returns_only_budget_rows(db):
    budget_a = _create_budget(db, name="A").reply["id"]
    budget_b = _create_budget(
        db, name="B", start="2026-06-01", end="2026-06-30"
    ).reply["id"]
    handlers.create_allocation(
        db,
        {"budget_id": budget_a, "category_id": 1, "planned_amount": "100.00"},
    )
    handlers.create_allocation(
        db,
        {"budget_id": budget_b, "category_id": 1, "planned_amount": "200.00"},
    )
    outcome = handlers.list_allocations(db, {"budget_id": budget_a})
    assert len(outcome.reply) == 1
    assert outcome.reply[0]["planned_amount"] == "100.00"


def test_list_allocations_empty(db):
    budget_id = _create_budget(db).reply["id"]
    outcome = handlers.list_allocations(db, {"budget_id": budget_id})
    assert outcome.reply == []


def test_update_allocation_changes_planned_amount(db):
    budget_id = _create_budget(db).reply["id"]
    allocation_id = handlers.create_allocation(
        db,
        {"budget_id": budget_id, "category_id": 1, "planned_amount": "100.00"},
    ).reply["id"]
    outcome = handlers.update_allocation(
        db,
        {
            "budget_id": budget_id,
            "allocation_id": allocation_id,
            "planned_amount": "150.00",
        },
    )
    assert outcome.reply["planned_amount"] == "150.00"


def test_delete_allocation_removes_it(db):
    budget_id = _create_budget(db).reply["id"]
    allocation_id = handlers.create_allocation(
        db,
        {"budget_id": budget_id, "category_id": 1, "planned_amount": "100.00"},
    ).reply["id"]
    handlers.delete_allocation(
        db, {"budget_id": budget_id, "allocation_id": allocation_id}
    )
    outcome = handlers.list_allocations(db, {"budget_id": budget_id})
    assert outcome.reply == []


def test_update_unknown_allocation_returns_404(db):
    budget_id = _create_budget(db).reply["id"]
    with pytest.raises(ServiceError) as exc:
        handlers.update_allocation(
            db,
            {
                "budget_id": budget_id,
                "allocation_id": 999,
                "planned_amount": "1.00",
            },
        )
    assert exc.value.status == 404


def test_allocation_under_wrong_budget_returns_404(db):
    budget_a = _create_budget(db, name="A").reply["id"]
    budget_b = _create_budget(
        db, name="B", start="2026-06-01", end="2026-06-30"
    ).reply["id"]
    allocation_id = handlers.create_allocation(
        db,
        {"budget_id": budget_a, "category_id": 1, "planned_amount": "100.00"},
    ).reply["id"]
    with pytest.raises(ServiceError) as exc:
        handlers.delete_allocation(
            db, {"budget_id": budget_b, "allocation_id": allocation_id}
        )
    assert exc.value.status == 404


def test_delete_budget_cascades_allocations(db):
    budget_id = _create_budget(db).reply["id"]
    handlers.create_allocation(
        db,
        {"budget_id": budget_id, "category_id": 1, "planned_amount": "100.00"},
    )
    handlers.delete_budget(db, {"budget_id": budget_id})
    # The budget is gone; the allocation was cascade-deleted with it.
    with pytest.raises(ServiceError):
        handlers.list_allocations(db, {"budget_id": budget_id})
