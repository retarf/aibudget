"""ORM models for transaction-service.

`Transaction` is the owned domain table. `BudgetProjection` and
`CategoryProjection` are local read-models maintained from `budget.*` /
`category.*` events and used to validate transaction references.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.schemas import CategoryKind, TransactionType

from .database import Base


class Transaction(Base):
    """An income or expense recorded within a budget and classified by category.

    `budget_id` and `category_id` reference rows owned by other services, so
    there is no SQL foreign key — referential integrity is maintained through
    validation against the projections and the delete cascades.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    budget_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)


class BudgetProjection(Base):
    """Local read-model of budgets, built from `budget.*` events."""

    __tablename__ = "budget_projection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)


class CategoryProjection(Base):
    """Local read-model of categories, built from `category.*` events."""

    __tablename__ = "category_projection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    kind: Mapped[CategoryKind] = mapped_column(
        Enum(CategoryKind), nullable=False
    )
