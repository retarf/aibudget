from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.category import CategoryKind
from backend.schemas.category import CategoryCreate, CategoryRead
from backend.services import category as service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return service.create_category(db, data)


@router.get("", response_model=list[CategoryRead])
def list_categories(
    kind: CategoryKind | None = None, db: Session = Depends(get_db)
):
    return service.list_categories(db, kind)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    service.delete_category(db, category_id)
