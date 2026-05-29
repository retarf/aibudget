"""ORM models for budget-service."""
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Budget(Base):
    """A time period in which a user records transactions.

    Transactions live in transaction-service; there is no ORM relationship to
    them here. Deleting a budget publishes ``budget.deleted``, which
    transaction-service consumes to cascade the cleanup.
    """

    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    allocations: Mapped[list["Allocation"]] = relationship(
        back_populates="budget",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Template(Base):
    """A reusable named blueprint of (category, planned_amount) line items."""

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    items: Mapped[list["TemplateItem"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TemplateItem(Base):
    """A single (category, planned_amount) entry of a template.

    ``category_id`` references a row owned by category-service, so there is no
    SQL foreign key — the cascade on category deletion runs via the
    ``category.deleted`` event.
    """

    __tablename__ = "template_items"
    __table_args__ = (
        UniqueConstraint(
            "template_id", "category_id", name="uq_template_items_template_category"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    planned_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    template: Mapped[Template] = relationship(back_populates="items")


class Allocation(Base):
    """A planned amount for a category within a specific budget.

    Like ``TemplateItem.category_id``, this references a row owned by
    category-service and carries no SQL foreign key.
    """

    __tablename__ = "allocations"
    __table_args__ = (
        UniqueConstraint(
            "budget_id", "category_id", name="uq_allocations_budget_category"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    budget_id: Mapped[int] = mapped_column(
        ForeignKey("budgets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    planned_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    budget: Mapped[Budget] = relationship(back_populates="allocations")
