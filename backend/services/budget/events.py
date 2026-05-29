"""Event consumers for budget-service.

Currently handles `category.deleted` to cascade-delete template line items
that reference the removed category. Allocations are intentionally not
cascaded: they record a historical planned amount and are valid even after
their category is gone (see design.md, Decision 5).
"""
from sqlalchemy import delete as sa_delete
from sqlalchemy.orm import Session

from .models import TemplateItem


def apply_event(db: Session, event: str, data: dict) -> None:
    """Dispatch a consumed event to the right handler."""
    if event == "category.deleted":
        _apply_category_deleted(db, data)


def _apply_category_deleted(db: Session, data: dict) -> None:
    category_id = data["id"]
    db.execute(
        sa_delete(TemplateItem).where(TemplateItem.category_id == category_id)
    )
    db.commit()
