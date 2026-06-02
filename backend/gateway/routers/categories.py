"""Category REST routes — served over NATS, with a cross-service delete guard.

A category may be deleted only when it is not in use. The gateway gathers usage
from transaction-service (transactions) and budget-service (allocations +
template items) to decide, to enrich the list, and to power Erase History — the
operation that purges a category's footprint so it can then be deleted.
"""

import asyncio

from fastapi import APIRouter, HTTPException, status

from backend.common.schemas import (
    CategoryCreate,
    CategoryKind,
    CategoryRead,
    CategoryWithUsage,
)

from ..nats_client import call

router = APIRouter(prefix="/categories", tags=["categories"])


async def _usage_for(category_id: int) -> dict:
    """Gather a category's usage across services into counts plus an in-use flag."""
    transactions, planning = await asyncio.gather(
        call("transaction.category.usage", {"category_id": category_id}),
        call("budget.category.usage", {"category_id": category_id}),
    )
    counts = {
        "transactions": transactions["transactions"],
        "allocations": planning["allocations"],
        "templates": planning["templates"],
    }
    return {"usage": counts, "in_use": sum(counts.values()) > 0}


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate):
    return await call("category.create", data.model_dump(mode="json"))


@router.get("", response_model=list[CategoryWithUsage])
async def list_categories(kind: CategoryKind | None = None):
    payload = {} if kind is None else {"kind": kind.value}
    categories = await call("category.list", payload)
    usages = await asyncio.gather(*(_usage_for(c["id"]) for c in categories))
    return [
        {**category, **usage}
        for category, usage in zip(categories, usages, strict=True)
    ]


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int):
    usage = await _usage_for(category_id)
    if usage["in_use"]:
        counts = usage["usage"]
        raise HTTPException(
            status_code=409,
            detail=(
                "Category is in use and cannot be deleted "
                f"({counts['transactions']} transactions, "
                f"{counts['allocations']} allocations, "
                f"{counts['templates']} templates). Erase its history first."
            ),
        )
    await call("category.delete", {"category_id": category_id})


@router.post("/{category_id}/erase-history", status_code=status.HTTP_204_NO_CONTENT)
async def erase_category_history(category_id: int):
    # Purge the category's footprint everywhere; both purges are idempotent, so
    # a re-run after a partial failure is safe.
    await asyncio.gather(
        call("transaction.category.purge", {"category_id": category_id}),
        call("budget.category.purge", {"category_id": category_id}),
    )
