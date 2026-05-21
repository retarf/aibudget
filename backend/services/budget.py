"""Business logic for budgets."""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.budget import Budget
from backend.schemas.budget import BudgetCreate, BudgetUpdate


def get_budget(db: Session, budget_id: int) -> Budget:
    """Return a budget or raise 404. Period validation lives in the schema."""
    budget = db.get(Budget, budget_id)
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found"
        )
    return budget


def create_budget(db: Session, data: BudgetCreate) -> Budget:
    budget = Budget(
        name=data.name, start_date=data.start_date, end_date=data.end_date
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def list_budgets(db: Session) -> list[Budget]:
    return list(db.scalars(select(Budget)))


def update_budget(db: Session, budget_id: int, data: BudgetUpdate) -> Budget:
    budget = get_budget(db, budget_id)
    budget.name = data.name
    budget.start_date = data.start_date
    budget.end_date = data.end_date
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget_id: int) -> None:
    budget = get_budget(db, budget_id)
    db.delete(budget)
    db.commit()
