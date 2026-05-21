from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from backend.services import budget as service

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(data: BudgetCreate, db: Session = Depends(get_db)):
    return service.create_budget(db, data)


@router.get("", response_model=list[BudgetRead])
def list_budgets(db: Session = Depends(get_db)):
    return service.list_budgets(db)


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    return service.get_budget(db, budget_id)


@router.put("/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: int, data: BudgetUpdate, db: Session = Depends(get_db)
):
    return service.update_budget(db, budget_id, data)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    service.delete_budget(db, budget_id)
