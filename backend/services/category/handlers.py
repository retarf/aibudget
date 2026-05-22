"""Request/reply handlers for category-service.

Ported from the monolith's ``backend/services/category.py``. The monolith's
"category is referenced by a transaction" check on delete is intentionally
dropped: category-service cannot see transactions. Cleanup happens via the
``category.deleted`` cascade in transaction-service (see design.md).
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.common.health import health_handler
from backend.common.messaging import Outcome, ServiceError
from backend.common.schemas import CategoryCreate, CategoryKind, CategoryRead

from .models import Category


def _read(category: Category) -> dict:
    """Serialize a category to a JSON-able dict for envelopes and events."""
    return CategoryRead.model_validate(category).model_dump(mode="json")


def create_category(db: Session, request: dict) -> Outcome:
    data = CategoryCreate.model_validate(request)
    existing = db.scalar(
        select(Category).where(
            Category.name == data.name, Category.kind == data.kind
        )
    )
    if existing is not None:
        raise ServiceError(
            409, "A category with this name already exists for this kind"
        )
    category = Category(name=data.name, kind=data.kind)
    db.add(category)
    db.commit()
    db.refresh(category)
    payload = _read(category)
    return Outcome(reply=payload, event_change="created", event_data=payload)


def list_categories(db: Session, request: dict) -> Outcome:
    stmt = select(Category)
    kind = request.get("kind")
    if kind is not None:
        stmt = stmt.where(Category.kind == CategoryKind(kind))
    return Outcome(reply=[_read(c) for c in db.scalars(stmt)])


def delete_category(db: Session, request: dict) -> Outcome:
    category = db.get(Category, request["category_id"])
    if category is None:
        raise ServiceError(404, "Category not found")
    category_id = category.id
    db.delete(category)
    db.commit()
    return Outcome(
        reply=None, event_change="deleted", event_data={"id": category_id}
    )


# Maps the operation name in a `category.<operation>` subject to its handler.
HANDLERS = {
    "create": create_category,
    "list": list_categories,
    "delete": delete_category,
    "health": health_handler,
}
