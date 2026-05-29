"""Request/reply handlers for budget-service.

Each handler is a sync ``fn(db, request) -> Outcome``: it performs the
operation and returns the reply payload plus, for state changes, the domain
event to publish. Ported from the monolith's ``backend/services/budget.py``,
with ``HTTPException`` replaced by ``ServiceError``.
"""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.common.health import health_handler
from backend.common.messaging import Outcome, ServiceError
from backend.common.schemas import (
    AllocationCreate,
    AllocationRead,
    AllocationUpdate,
    BudgetCreate,
    BudgetRead,
    BudgetUpdate,
    TemplateCreate,
    TemplateDetailRead,
    TemplateItemCreate,
    TemplateItemRead,
    TemplateRead,
    TemplateUpdate,
)

from .models import Allocation, Budget, Template, TemplateItem


def _read(budget: Budget) -> dict:
    """Serialize a budget to a JSON-able dict for envelopes and events."""
    return BudgetRead.model_validate(budget).model_dump(mode="json")


def _read_template(template: Template) -> dict:
    return TemplateRead.model_validate(template).model_dump(mode="json")


def _read_template_detail(template: Template) -> dict:
    return TemplateDetailRead.model_validate(template).model_dump(mode="json")


def _read_template_item(item: TemplateItem) -> dict:
    return TemplateItemRead.model_validate(item).model_dump(mode="json")


def _read_allocation(allocation: Allocation) -> dict:
    return AllocationRead.model_validate(allocation).model_dump(mode="json")


def _get(db: Session, budget_id: int) -> Budget:
    budget = db.get(Budget, budget_id)
    if budget is None:
        raise ServiceError(404, "Budget not found")
    return budget


def _get_template(db: Session, template_id: int) -> Template:
    template = db.get(Template, template_id)
    if template is None:
        raise ServiceError(404, "Template not found")
    return template


def _get_template_item(
    db: Session, template_id: int, item_id: int
) -> TemplateItem:
    item = db.get(TemplateItem, item_id)
    if item is None or item.template_id != template_id:
        raise ServiceError(404, "Template item not found")
    return item


def _get_allocation(
    db: Session, budget_id: int, allocation_id: int
) -> Allocation:
    allocation = db.get(Allocation, allocation_id)
    if allocation is None or allocation.budget_id != budget_id:
        raise ServiceError(404, "Allocation not found")
    return allocation


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


# --- templates ---------------------------------------------------------------

def create_template(db: Session, request: dict) -> Outcome:
    data = TemplateCreate.model_validate(request)
    template = Template(name=data.name)
    db.add(template)
    db.commit()
    db.refresh(template)
    return Outcome(reply=_read_template(template))


def list_templates(db: Session, request: dict) -> Outcome:
    templates = db.scalars(select(Template))
    return Outcome(reply=[_read_template(t) for t in templates])


def get_template(db: Session, request: dict) -> Outcome:
    template = _get_template(db, request["template_id"])
    return Outcome(reply=_read_template_detail(template))


def update_template(db: Session, request: dict) -> Outcome:
    template = _get_template(db, request["template_id"])
    data = TemplateUpdate.model_validate(request)
    template.name = data.name
    db.commit()
    db.refresh(template)
    return Outcome(reply=_read_template(template))


def delete_template(db: Session, request: dict) -> Outcome:
    template = _get_template(db, request["template_id"])
    db.delete(template)
    db.commit()
    return Outcome(reply=None)


def add_template_item(db: Session, request: dict) -> Outcome:
    template = _get_template(db, request["template_id"])
    data = TemplateItemCreate.model_validate(request)
    existing = db.scalar(
        select(TemplateItem).where(
            TemplateItem.template_id == template.id,
            TemplateItem.category_id == data.category_id,
        )
    )
    if existing is not None:
        raise ServiceError(409, "Category already in template")
    item = TemplateItem(
        template_id=template.id,
        category_id=data.category_id,
        planned_amount=data.planned_amount,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ServiceError(409, "Category already in template")
    db.refresh(item)
    return Outcome(reply=_read_template_item(item))


def delete_template_item(db: Session, request: dict) -> Outcome:
    item = _get_template_item(
        db, request["template_id"], request["item_id"]
    )
    db.delete(item)
    db.commit()
    return Outcome(reply=None)


def apply_template(db: Session, request: dict) -> Outcome:
    budget = _get(db, request["budget_id"])
    template = _get_template(db, request["template_id"])
    items = db.scalars(
        select(TemplateItem).where(TemplateItem.template_id == template.id)
    ).all()
    existing_categories = {
        row
        for row in db.scalars(
            select(Allocation.category_id).where(
                Allocation.budget_id == budget.id
            )
        )
    }
    created: list[Allocation] = []
    for item in items:
        if item.category_id in existing_categories:
            continue
        allocation = Allocation(
            budget_id=budget.id,
            category_id=item.category_id,
            planned_amount=item.planned_amount,
        )
        db.add(allocation)
        created.append(allocation)
    db.commit()
    for allocation in created:
        db.refresh(allocation)
    return Outcome(reply=[_read_allocation(a) for a in created])


# --- allocations -------------------------------------------------------------

def create_allocation(db: Session, request: dict) -> Outcome:
    budget = _get(db, request["budget_id"])
    data = AllocationCreate.model_validate(request)
    existing = db.scalar(
        select(Allocation).where(
            Allocation.budget_id == budget.id,
            Allocation.category_id == data.category_id,
        )
    )
    if existing is not None:
        raise ServiceError(409, "Allocation already exists for this category")
    allocation = Allocation(
        budget_id=budget.id,
        category_id=data.category_id,
        planned_amount=data.planned_amount,
    )
    db.add(allocation)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ServiceError(409, "Allocation already exists for this category")
    db.refresh(allocation)
    return Outcome(reply=_read_allocation(allocation))


def list_allocations(db: Session, request: dict) -> Outcome:
    budget = _get(db, request["budget_id"])
    allocations = db.scalars(
        select(Allocation).where(Allocation.budget_id == budget.id)
    )
    return Outcome(reply=[_read_allocation(a) for a in allocations])


def update_allocation(db: Session, request: dict) -> Outcome:
    allocation = _get_allocation(
        db, request["budget_id"], request["allocation_id"]
    )
    data = AllocationUpdate.model_validate(request)
    allocation.planned_amount = data.planned_amount
    db.commit()
    db.refresh(allocation)
    return Outcome(reply=_read_allocation(allocation))


def delete_allocation(db: Session, request: dict) -> Outcome:
    allocation = _get_allocation(
        db, request["budget_id"], request["allocation_id"]
    )
    db.delete(allocation)
    db.commit()
    return Outcome(reply=None)


# Maps the operation name in a `budget.<operation>` subject to its handler.
# Multi-part operations (e.g. "template.create") resolve to dotted subjects
# such as ``budget.template.create``.
HANDLERS = {
    "create": create_budget,
    "list": list_budgets,
    "get": get_budget,
    "update": update_budget,
    "delete": delete_budget,
    "health": health_handler,
    "template.create": create_template,
    "template.list": list_templates,
    "template.get": get_template,
    "template.update": update_template,
    "template.delete": delete_template,
    "template.item.add": add_template_item,
    "template.item.delete": delete_template_item,
    "template.apply": apply_template,
    "allocation.create": create_allocation,
    "allocation.list": list_allocations,
    "allocation.update": update_allocation,
    "allocation.delete": delete_allocation,
}
