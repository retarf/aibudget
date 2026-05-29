"""Template REST routes — translated to budget-service over NATS."""
from fastapi import APIRouter, status

from backend.common.schemas import (
    AllocationRead,
    ApplyTemplateRequest,
    TemplateCreate,
    TemplateDetailRead,
    TemplateItemCreate,
    TemplateItemRead,
    TemplateRead,
    TemplateUpdate,
)

from ..nats_client import call

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post(
    "", response_model=TemplateRead, status_code=status.HTTP_201_CREATED
)
async def create_template(data: TemplateCreate):
    return await call("budget.template.create", data.model_dump(mode="json"))


@router.get("", response_model=list[TemplateRead])
async def list_templates():
    return await call("budget.template.list", {})


@router.get("/{template_id}", response_model=TemplateDetailRead)
async def get_template(template_id: int):
    return await call("budget.template.get", {"template_id": template_id})


@router.put("/{template_id}", response_model=TemplateRead)
async def update_template(template_id: int, data: TemplateUpdate):
    return await call(
        "budget.template.update",
        {"template_id": template_id, **data.model_dump(mode="json")},
    )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: int):
    await call("budget.template.delete", {"template_id": template_id})


@router.post(
    "/{template_id}/items",
    response_model=TemplateItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_template_item(template_id: int, data: TemplateItemCreate):
    return await call(
        "budget.template.item.add",
        {"template_id": template_id, **data.model_dump(mode="json")},
    )


@router.delete(
    "/{template_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template_item(template_id: int, item_id: int):
    await call(
        "budget.template.item.delete",
        {"template_id": template_id, "item_id": item_id},
    )


apply_router = APIRouter(tags=["templates"])


@apply_router.post(
    "/budgets/{budget_id}/apply-template",
    response_model=list[AllocationRead],
)
async def apply_template(budget_id: int, data: ApplyTemplateRequest):
    return await call(
        "budget.template.apply",
        {"budget_id": budget_id, "template_id": data.template_id},
    )
