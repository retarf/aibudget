"""Tests for budget-service handlers."""
import pytest

from backend.common.messaging import ServiceError
from backend.services.budget import handlers


def _create(db, name="May", start="2026-05-01", end="2026-05-31"):
    return handlers.create_budget(
        db, {"name": name, "start_date": start, "end_date": end}
    )


def test_create_returns_budget_and_event(db):
    outcome = _create(db)
    assert outcome.reply["name"] == "May"
    assert outcome.event_change == "created"
    assert outcome.event_data["id"] == outcome.reply["id"]


def test_list_returns_all_budgets(db):
    _create(db, "A")
    _create(db, "B")
    outcome = handlers.list_budgets(db, {})
    assert {b["name"] for b in outcome.reply} == {"A", "B"}
    assert outcome.event_change is None


def test_get_unknown_budget_raises_404(db):
    with pytest.raises(ServiceError) as exc:
        handlers.get_budget(db, {"budget_id": 999})
    assert exc.value.status == 404


def test_update_changes_fields_and_emits_event(db):
    budget_id = _create(db).reply["id"]
    outcome = handlers.update_budget(
        db,
        {
            "budget_id": budget_id,
            "name": "June",
            "start_date": "2026-06-01",
            "end_date": "2026-06-30",
        },
    )
    assert outcome.reply["name"] == "June"
    assert outcome.event_change == "updated"


def test_delete_removes_budget_and_emits_event(db):
    budget_id = _create(db).reply["id"]
    outcome = handlers.delete_budget(db, {"budget_id": budget_id})
    assert outcome.event_change == "deleted"
    assert outcome.event_data == {"id": budget_id}
    with pytest.raises(ServiceError):
        handlers.get_budget(db, {"budget_id": budget_id})


def test_health_handler_reports_ok(db):
    assert handlers.HANDLERS["health"](db, {}).reply == {"status": "ok"}
