"""SQLAlchemy engine, session factory, and base for transaction-service.

transaction-service owns this database exclusively (database-per-service). It
holds the `transactions` table plus the `budget_projection` /
`category_projection` read-models built from other services' events.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Each service container is given a DATABASE_URL pointing at its own database.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://aibudget:change-me@transaction-db:5432/transaction",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base for transaction-service ORM models."""


def init_db() -> None:
    """Create tables on startup. No migration tool yet — see design.md."""
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
