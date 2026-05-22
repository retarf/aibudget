"""Budget REST routes — same contract as the monolith, served over NATS."""
from fastapi import APIRouter, status

from backend.common.schemas import BudgetCreate, BudgetRead, BudgetUpdate

from ..nats_client import call

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
async def create_budget(data: BudgetCreate):
    return await call("budget.create", data.model_dump(mode="json"))


@router.get("", response_model=list[BudgetRead])
async def list_budgets():
    return await call("budget.list", {})


@router.get("/{budget_id}", response_model=BudgetRead)
async def get_budget(budget_id: int):
    return await call("budget.get", {"budget_id": budget_id})


@router.put("/{budget_id}", response_model=BudgetRead)
async def update_budget(budget_id: int, data: BudgetUpdate):
    return await call(
        "budget.update", {"budget_id": budget_id, **data.model_dump(mode="json")}
    )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(budget_id: int):
    await call("budget.delete", {"budget_id": budget_id})
