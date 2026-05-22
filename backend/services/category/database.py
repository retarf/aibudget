"""SQLAlchemy engine, session factory, and base for category-service.

category-service owns this database exclusively (database-per-service); no
other service connects to it.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Each service container is given a DATABASE_URL pointing at its own database.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://aibudget:change-me@category-db:5432/category",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base for category-service ORM models."""


def init_db() -> None:
    """Create tables on startup. No migration tool yet — see design.md."""
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
