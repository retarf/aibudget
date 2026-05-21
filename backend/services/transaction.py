"""Business logic for transactions."""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.budget import Budget
from backend.models.category import Category
from backend.models.transaction import Transaction
from backend.schemas.transaction import TransactionCreate, TransactionUpdate


def _get_budget(db: Session, budget_id: int) -> Budget:
    budget = db.get(Budget, budget_id)
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found"
        )
    return budget


def get_transaction(db: Session, transaction_id: int) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return transaction


def _validate(db: Session, budget: Budget, data: TransactionCreate) -> None:
    """Domain rules beyond field validation (amount > 0 is enforced by schema)."""
    if not budget.start_date <= data.date <= budget.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Transaction date is outside the budget period",
        )
    if db.get(Category, data.category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Category does not exist",
        )


def create_transaction(
    db: Session, budget_id: int, data: TransactionCreate
) -> Transaction:
    budget = _get_budget(db, budget_id)
    _validate(db, budget, data)
    transaction = Transaction(
        budget_id=budget.id,
        category_id=data.category_id,
        type=data.type,
        amount=data.amount,
        date=data.date,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def list_transactions(db: Session, budget_id: int) -> list[Transaction]:
    _get_budget(db, budget_id)
    return list(
        db.scalars(
            select(Transaction).where(Transaction.budget_id == budget_id)
        )
    )


def update_transaction(
    db: Session, transaction_id: int, data: TransactionUpdate
) -> Transaction:
    transaction = get_transaction(db, transaction_id)
    budget = _get_budget(db, transaction.budget_id)
    _validate(db, budget, data)
    transaction.type = data.type
    transaction.amount = data.amount
    transaction.date = data.date
    transaction.category_id = data.category_id
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction_id: int) -> None:
    transaction = get_transaction(db, transaction_id)
    db.delete(transaction)
    db.commit()
