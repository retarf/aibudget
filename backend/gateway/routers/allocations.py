"""Planned allocation REST routes — translated to budget-service over NATS."""
from fastapi import APIRouter, status

from backend.common.schemas import (
    AllocationCreate,
    AllocationRead,
    AllocationUpdate,
)

from ..nats_client import call

router = APIRouter(tags=["allocations"])


@router.get(
    "/budgets/{budget_id}/allocations",
    response_model=list[AllocationRead],
)
async def list_allocations(budget_id: int):
    return await call("budget.allocation.list", {"budget_id": budget_id})


@router.post(
    "/budgets/{budget_id}/allocations",
    response_model=AllocationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_allocation(budget_id: int, data: AllocationCreate):
    return await call(
        "budget.allocation.create",
        {"budget_id": budget_id, **data.model_dump(mode="json")},
    )


@router.put(
    "/budgets/{budget_id}/allocations/{allocation_id}",
    response_model=AllocationRead,
)
async def update_allocation(
    budget_id: int, allocation_id: int, data: AllocationUpdate
):
    return await call(
        "budget.allocation.update",
        {
            "budget_id": budget_id,
            "allocation_id": allocation_id,
            **data.model_dump(mode="json"),
        },
    )


@router.delete(
    "/budgets/{budget_id}/allocations/{allocation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_allocation(budget_id: int, allocation_id: int):
    await call(
        "budget.allocation.delete",
        {"budget_id": budget_id, "allocation_id": allocation_id},
    )
