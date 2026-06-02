"""Tests for budget-service category usage / purge handlers."""

from backend.services.budget import handlers
from backend.services.budget.models import Allocation, TemplateItem
from sqlalchemy import select


def _create_budget(db, name="May", start="2026-05-01", end="2026-05-31"):
    return handlers.create_budget(
        db, {"name": name, "start_date": start, "end_date": end}
    )


def _seed_allocation(db, budget_id, category_id, amount="100.00"):
    return handlers.create_allocation(
        db,
        {"budget_id": budget_id, "category_id": category_id, "planned_amount": amount},
    )


def _seed_template_item(db, category_id, amount="200.00", name="Monthly"):
    template_id = handlers.create_template(db, {"name": name}).reply["id"]
    handlers.add_template_item(
        db,
        {
            "template_id": template_id,
            "category_id": category_id,
            "planned_amount": amount,
        },
    )
    return template_id


def test_category_usage_counts_allocations_and_template_items(db):
    budget_id = _create_budget(db).reply["id"]
    _seed_allocation(db, budget_id, category_id=1)
    _seed_template_item(db, category_id=1)
    outcome = handlers.category_usage(db, {"category_id": 1})
    assert outcome.reply == {"allocations": 1, "templates": 1}


def test_category_usage_zero_for_unused_category(db):
    outcome = handlers.category_usage(db, {"category_id": 999})
    assert outcome.reply == {"allocations": 0, "templates": 0}


def test_purge_category_deletes_allocations_and_template_items(db):
    budget_id = _create_budget(db).reply["id"]
    _seed_allocation(db, budget_id, category_id=1)
    _seed_allocation(db, budget_id, category_id=2)
    _seed_template_item(db, category_id=1)
    _seed_template_item(db, category_id=2, name="Other")

    handlers.purge_category(db, {"category_id": 1})

    allocations = [a.category_id for a in db.scalars(select(Allocation))]
    items = [i.category_id for i in db.scalars(select(TemplateItem))]
    assert allocations == [2]
    assert items == [2]


def test_purge_category_is_idempotent(db):
    handlers.purge_category(db, {"category_id": 1})  # nothing to delete
    outcome = handlers.purge_category(db, {"category_id": 1})
    assert outcome.reply is None
