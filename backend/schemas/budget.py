from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
