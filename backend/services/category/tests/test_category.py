"""Tests for category-service handlers."""
import pytest

from backend.common.messaging import ServiceError
from backend.services.category import handlers


def _create(db, name="Rent", kind="expense"):
    return handlers.create_category(db, {"name": name, "kind": kind})


def test_create_returns_category_and_event(db):
    outcome = _create(db)
    assert outcome.reply["name"] == "Rent"
    assert outcome.reply["kind"] == "expense"
    assert outcome.event_change == "created"


def test_create_rejects_duplicate_name_and_kind(db):
    _create(db)
    with pytest.raises(ServiceError) as exc:
        _create(db)
    assert exc.value.status == 409


def test_same_name_allowed_across_kinds(db):
    _create(db, "Bonus", "income")
    outcome = _create(db, "Bonus", "expense")
    assert outcome.reply["kind"] == "expense"


def test_list_filters_by_kind(db):
    _create(db, "Rent", "expense")
    _create(db, "Salary", "income")
    incomes = handlers.list_categories(db, {"kind": "income"})
    assert [c["name"] for c in incomes.reply] == ["Salary"]


def test_delete_unknown_category_raises_404(db):
    with pytest.raises(ServiceError) as exc:
        handlers.delete_category(db, {"category_id": 999})
    assert exc.value.status == 404


def test_delete_succeeds_and_emits_event(db):
    category_id = _create(db).reply["id"]
    outcome = handlers.delete_category(db, {"category_id": category_id})
    assert outcome.event_change == "deleted"
    assert outcome.event_data == {"id": category_id}
