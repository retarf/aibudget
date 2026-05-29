"""Tests for budget-service template handlers."""
import pytest

from backend.common.messaging import ServiceError
from backend.services.budget import handlers


def _create_template(db, name="Monthly"):
    return handlers.create_template(db, {"name": name})


def _create_budget(db, name="May", start="2026-05-01", end="2026-05-31"):
    return handlers.create_budget(
        db, {"name": name, "start_date": start, "end_date": end}
    )


def test_create_template_returns_template(db):
    outcome = _create_template(db)
    assert outcome.reply["name"] == "Monthly"
    assert "id" in outcome.reply
    assert outcome.event_change is None


def test_list_templates_returns_all(db):
    _create_template(db, "A")
    _create_template(db, "B")
    outcome = handlers.list_templates(db, {})
    assert {t["name"] for t in outcome.reply} == {"A", "B"}


def test_get_template_returns_items(db):
    template_id = _create_template(db).reply["id"]
    handlers.add_template_item(
        db,
        {"template_id": template_id, "category_id": 1, "planned_amount": "10.00"},
    )
    outcome = handlers.get_template(db, {"template_id": template_id})
    assert outcome.reply["name"] == "Monthly"
    assert len(outcome.reply["items"]) == 1
    assert outcome.reply["items"][0]["category_id"] == 1
    assert outcome.reply["items"][0]["planned_amount"] == "10.00"


def test_get_unknown_template_raises_404(db):
    with pytest.raises(ServiceError) as exc:
        handlers.get_template(db, {"template_id": 999})
    assert exc.value.status == 404


def test_update_template_changes_name(db):
    template_id = _create_template(db).reply["id"]
    outcome = handlers.update_template(
        db, {"template_id": template_id, "name": "Annual"}
    )
    assert outcome.reply["name"] == "Annual"


def test_delete_template_removes_items(db):
    template_id = _create_template(db).reply["id"]
    handlers.add_template_item(
        db,
        {"template_id": template_id, "category_id": 1, "planned_amount": "10.00"},
    )
    handlers.delete_template(db, {"template_id": template_id})
    with pytest.raises(ServiceError):
        handlers.get_template(db, {"template_id": template_id})


def test_add_template_item_duplicate_returns_409(db):
    template_id = _create_template(db).reply["id"]
    handlers.add_template_item(
        db,
        {"template_id": template_id, "category_id": 1, "planned_amount": "10.00"},
    )
    with pytest.raises(ServiceError) as exc:
        handlers.add_template_item(
            db,
            {
                "template_id": template_id,
                "category_id": 1,
                "planned_amount": "20.00",
            },
        )
    assert exc.value.status == 409


def test_delete_template_item_removes_it(db):
    template_id = _create_template(db).reply["id"]
    item_id = handlers.add_template_item(
        db,
        {"template_id": template_id, "category_id": 1, "planned_amount": "10.00"},
    ).reply["id"]
    handlers.delete_template_item(
        db, {"template_id": template_id, "item_id": item_id}
    )
    outcome = handlers.get_template(db, {"template_id": template_id})
    assert outcome.reply["items"] == []


def test_apply_template_to_empty_budget_creates_allocations(db):
    budget_id = _create_budget(db).reply["id"]
    template_id = _create_template(db).reply["id"]
    handlers.add_template_item(
        db,
        {"template_id": template_id, "category_id": 1, "planned_amount": "100.00"},
    )
    handlers.add_template_item(
        db,
        {"template_id": template_id, "category_id": 2, "planned_amount": "200.00"},
    )
    outcome = handlers.apply_template(
        db, {"budget_id": budget_id, "template_id": template_id}
    )
    assert len(outcome.reply) == 2

    listed = handlers.list_allocations(db, {"budget_id": budget_id}).reply
    by_category = {a["category_id"]: a["planned_amount"] for a in listed}
    assert by_category == {1: "100.00", 2: "200.00"}


def test_apply_template_merges_existing_allocations(db):
    budget_id = _create_budget(db).reply["id"]
    handlers.create_allocation(
        db,
        {"budget_id": budget_id, "category_id": 1, "planned_amount": "999.00"},
    )
    template_id = _create_template(db).reply["id"]
    handlers.add_template_item(
        db,
        {"template_id": template_id, "category_id": 1, "planned_amount": "100.00"},
    )
    handlers.add_template_item(
        db,
        {"template_id": template_id, "category_id": 2, "planned_amount": "200.00"},
    )

    outcome = handlers.apply_template(
        db, {"budget_id": budget_id, "template_id": template_id}
    )
    # Only the new allocation was created; the existing one was kept.
    assert len(outcome.reply) == 1
    assert outcome.reply[0]["category_id"] == 2

    listed = handlers.list_allocations(db, {"budget_id": budget_id}).reply
    by_category = {a["category_id"]: a["planned_amount"] for a in listed}
    assert by_category == {1: "999.00", 2: "200.00"}


def test_apply_unknown_template_returns_404(db):
    budget_id = _create_budget(db).reply["id"]
    with pytest.raises(ServiceError) as exc:
        handlers.apply_template(
            db, {"budget_id": budget_id, "template_id": 999}
        )
    assert exc.value.status == 404


def test_apply_to_unknown_budget_returns_404(db):
    template_id = _create_template(db).reply["id"]
    with pytest.raises(ServiceError) as exc:
        handlers.apply_template(
            db, {"budget_id": 999, "template_id": template_id}
        )
    assert exc.value.status == 404
