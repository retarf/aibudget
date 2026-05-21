from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Budget(Base):
    """A time period in which a user records transactions."""

    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Deleting a budget removes its transactions.
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="budget",
        cascade="all, delete-orphan",
    )
