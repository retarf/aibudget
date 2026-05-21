from pydantic import BaseModel, ConfigDict, Field

from backend.models.category import CategoryKind


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
