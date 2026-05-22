"""Category REST routes — same contract as the monolith, served over NATS."""
from fastapi import APIRouter, status

from backend.common.schemas import CategoryCreate, CategoryKind, CategoryRead

from ..nats_client import call

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "", response_model=CategoryRead, status_code=status.HTTP_201_CREATED
)
async def create_category(data: CategoryCreate):
    return await call("category.create", data.model_dump(mode="json"))


@router.get("", response_model=list[CategoryRead])
async def list_categories(kind: CategoryKind | None = None):
    payload = {} if kind is None else {"kind": kind.value}
    return await call("category.list", payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int):
    await call("category.delete", {"category_id": category_id})
