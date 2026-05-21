from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from backend.services import transaction as service

# Transactions are created/listed under a budget, but addressed directly by id
# for retrieve/update/delete.
router = APIRouter(tags=["transactions"])


@router.post(
    "/budgets/{budget_id}/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    budget_id: int, data: TransactionCreate, db: Session = Depends(get_db)
):
    return service.create_transaction(db, budget_id, data)


@router.get(
    "/budgets/{budget_id}/transactions", response_model=list[TransactionRead]
)
def list_transactions(budget_id: int, db: Session = Depends(get_db)):
    return service.list_transactions(db, budget_id)


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    return service.get_transaction(db, transaction_id)


@router.put("/transactions/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int, data: TransactionUpdate, db: Session = Depends(get_db)
):
    return service.update_transaction(db, transaction_id, data)


@router.delete(
    "/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    service.delete_transaction(db, transaction_id)
