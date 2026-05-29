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


# --- templates ---------------------------------------------------------------

class TemplateCreate(BaseModel):
    """Request body for creating a budget template."""

    name: str = Field(min_length=1, max_length=100)


class TemplateUpdate(BaseModel):
    """Request body for updating a template's name."""

    name: str = Field(min_length=1, max_length=100)


class TemplateItemCreate(BaseModel):
    """Request body for adding a line item to a template."""

    category_id: int
    planned_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class TemplateItemRead(BaseModel):
    """A single template line item as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    planned_amount: Decimal


class TemplateRead(BaseModel):
    """A template summary (without line items) as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TemplateDetailRead(BaseModel):
    """A template with its full list of line items."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    items: list[TemplateItemRead]


class ApplyTemplateRequest(BaseModel):
    """Request body for applying a template to a budget."""

    template_id: int


# --- allocations -------------------------------------------------------------

class AllocationCreate(BaseModel):
    """Request body for creating a planned allocation on a budget."""

    category_id: int
    planned_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class AllocationUpdate(BaseModel):
    """Request body for updating the planned amount on an allocation."""

    planned_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class AllocationRead(BaseModel):
    """A planned allocation as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    budget_id: int
    category_id: int
    planned_amount: Decimal


# --- summary -----------------------------------------------------------------

class BudgetSummaryTotals(BaseModel):
    """Planned vs actual income/expense totals for a single budget."""

    planned_income: Decimal
    actual_income: Decimal
    planned_expense: Decimal
    actual_expense: Decimal
    net: Decimal


class BudgetSummaryCategory(BaseModel):
    """Planned vs actual amounts for a single category within a budget."""

    category_id: int
    kind: CategoryKind
    planned_amount: Decimal
    actual_amount: Decimal


class BudgetSummary(BaseModel):
    """Planned vs actual summary of a budget at aggregate and category level."""

    budget_id: int
    totals: BudgetSummaryTotals
    categories: list[BudgetSummaryCategory]


class CategorySummary(BaseModel):
    """A single (category, kind) actual-sum row from transaction-service."""

    category_id: int
    kind: CategoryKind
    income: Decimal
    expense: Decimal
