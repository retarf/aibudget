import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class TransactionType(str, enum.Enum):
    """Whether a transaction is an income or an expense."""

    income = "income"
    expense = "expense"


class Transaction(Base):
    """An income or expense recorded within a budget and classified by category."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    budget_id: Mapped[int] = mapped_column(
        ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    budget: Mapped["Budget"] = relationship(back_populates="transactions")
    category: Mapped["Category"] = relationship()
