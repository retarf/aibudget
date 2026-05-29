"""aibudget API gateway — FastAPI application entry point.

Exposes the same REST contract as the monolith and translates each request
into a NATS request/reply call to the owning domain service.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .nats_client import close_nats, connect_nats, health_check
from .routers import allocations, budgets, categories, templates, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Open the NATS connection on startup, drain it on shutdown.
    await connect_nats()
    yield
    await close_nats()


app = FastAPI(title="aibudget API gateway", lifespan=lifespan)

# Allow the browser frontend (a different origin) to call the API.
_cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router)
app.include_router(budgets.router)
app.include_router(transactions.router)
app.include_router(templates.router)
app.include_router(templates.apply_router)
app.include_router(allocations.router)


@app.get("/health", tags=["health"])
async def health() -> dict:
    """Healthy only when NATS and every domain service respond."""
    return await health_check()
