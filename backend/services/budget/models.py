"""ORM models for budget-service."""
from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

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
