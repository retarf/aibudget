"""aibudget REST API — FastAPI application entry point."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import models  # noqa: F401  (registers ORM models on Base.metadata)
from backend.database import Base, engine
from backend.routers import budgets, categories, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup. No migration tool yet — see design.md.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="aibudget API", lifespan=lifespan)

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


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
