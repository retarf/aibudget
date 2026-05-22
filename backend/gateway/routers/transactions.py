"""Transaction REST routes — same contract as the monolith, served over NATS.

Transactions are created/listed under a budget, but addressed directly by id
for retrieve/update/delete.
"""
from fastapi import APIRouter, status

from backend.common.schemas import TransactionCreate, TransactionRead, TransactionUpdate

from ..nats_client import call

router = APIRouter(tags=["transactions"])


@router.post(
    "/budgets/{budget_id}/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(budget_id: int, data: TransactionCreate):
    return await call(
        "transaction.create",
        {"budget_id": budget_id, **data.model_dump(mode="json")},
    )


@router.get(
    "/budgets/{budget_id}/transactions", response_model=list[TransactionRead]
)
async def list_transactions(budget_id: int):
    return await call("transaction.list", {"budget_id": budget_id})


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
async def get_transaction(transaction_id: int):
    return await call(
        "transaction.get", {"transaction_id": transaction_id}
    )


@router.put("/transactions/{transaction_id}", response_model=TransactionRead)
async def update_transaction(transaction_id: int, data: TransactionUpdate):
    return await call(
        "transaction.update",
        {"transaction_id": transaction_id, **data.model_dump(mode="json")},
    )


@router.delete(
    "/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_transaction(transaction_id: int):
    await call("transaction.delete", {"transaction_id": transaction_id})
