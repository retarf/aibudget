"""Tests for budget-service event consumers (category.deleted cascade)."""
from sqlalchemy import select

from backend.services.budget import events, handlers
from backend.services.budget.models import TemplateItem


def _make_template_with_items(db, items):
    template_id = handlers.create_template(db, {"name": "T"}).reply["id"]
    for category_id, amount in items:
        handlers.add_template_item(
            db,
            {
                "template_id": template_id,
                "category_id": category_id,
                "planned_amount": amount,
            },
        )
    return template_id


def test_category_deleted_removes_matching_template_items(db):
    template_id = _make_template_with_items(
        db, [(1, "10.00"), (2, "20.00")]
    )

    events.apply_event(db, "category.deleted", {"id": 1})

    remaining = db.scalars(
        select(TemplateItem).where(TemplateItem.template_id == template_id)
    ).all()
    assert [item.category_id for item in remaining] == [2]


def test_category_deleted_leaves_other_categories_alone(db):
    template_a = _make_template_with_items(db, [(1, "10.00"), (2, "20.00")])
    template_b = _make_template_with_items(db, [(2, "30.00")])

    events.apply_event(db, "category.deleted", {"id": 1})

    remaining = db.scalars(select(TemplateItem)).all()
    by_template = {(item.template_id, item.category_id) for item in remaining}
    assert by_template == {(template_a, 2), (template_b, 2)}


def test_category_deleted_with_no_matches_is_noop(db):
    _make_template_with_items(db, [(1, "10.00")])
    events.apply_event(db, "category.deleted", {"id": 999})
    assert db.scalars(select(TemplateItem)).all() != []
