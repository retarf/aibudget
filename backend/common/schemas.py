"""Domain enums and Pydantic request/response schemas.

Shared by the gateway (as FastAPI request/response models, so invalid bodies
still yield 422) and by the services (to validate NATS payloads and shape
replies). ORM models live per-service; only these transport types are shared.
"""
import enum
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CategoryKind(str, enum.Enum):
    """Whether a category classifies incomes or expenses."""

    income = "income"
    expense = "expense"


class TransactionType(str, enum.Enum):
    """Whether a transaction is an income or an expense."""

    income = "income"
    expense = "expense"


# --- budget ------------------------------------------------------------------

class _BudgetInput(BaseModel):
    """Shared request fields for creating or updating a budget."""

    name: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def _check_period(self) -> "_BudgetInput":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class BudgetCreate(_BudgetInput):
    """Request body for creating a budget."""


class BudgetUpdate(_BudgetInput):
    """Request body for updating a budget."""


class BudgetRead(BaseModel):
    """Budget as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    start_date: date
    end_date: date


# --- category ----------------------------------------------------------------

class CategoryCreate(BaseModel):
    """Request body for creating a category."""

    name: str = Field(min_length=1, max_length=100)
    kind: CategoryKind


class CategoryRead(BaseModel):
    """Category as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    kind: CategoryKind


# --- transaction -------------------------------------------------------------

class _TransactionInput(BaseModel):
    """Shared request fields for recording or updating a transaction."""

    type: TransactionType
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    date: date
    category_id: int


class TransactionCreate(_TransactionInput):
    """Request body for recording a transaction."""


class TransactionUpdate(_TransactionInput):
    """Request body for updating a transaction."""


class TransactionRead(BaseModel):
    """Transaction as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    budget_id: int
    category_id: int
    type: TransactionType
    amount: Decimal
    date: date


# --- summary -----------------------------------------------------------------

class BudgetSummaryTotals(BaseModel):
    """Income, expense and net totals for a single budget."""

    income: Decimal
    expense: Decimal
    net: Decimal


class BudgetSummary(BaseModel):
    """Aggregated summary of a budget's transactions."""

    budget_id: int
    totals: BudgetSummaryTotals
