from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from backend.models.transaction import TransactionType


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
