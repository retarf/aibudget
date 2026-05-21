"""Business logic for categories."""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.category import Category, CategoryKind
from backend.models.transaction import Transaction
from backend.schemas.category import CategoryCreate


def create_category(db: Session, data: CategoryCreate) -> Category:
    existing = db.scalar(
        select(Category).where(
            Category.name == data.name, Category.kind == data.kind
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists for this kind",
        )
    category = Category(name=data.name, kind=data.kind)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def list_categories(
    db: Session, kind: CategoryKind | None = None
) -> list[Category]:
    stmt = select(Category)
    if kind is not None:
        stmt = stmt.where(Category.kind == kind)
    return list(db.scalars(stmt))


def delete_category(db: Session, category_id: int) -> None:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    in_use = db.scalar(
        select(Transaction).where(Transaction.category_id == category_id)
    )
    if in_use is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category is referenced by a transaction",
        )
    db.delete(category)
    db.commit()
