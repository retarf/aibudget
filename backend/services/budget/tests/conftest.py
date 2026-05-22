"""Test fixtures for budget-service.

Each test gets an isolated in-memory SQLite database; handlers are called
directly with the session, bypassing the NATS layer.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.services.budget import models  # noqa: F401  (registers ORM models)
from backend.services.budget.database import Base


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # one shared connection -> the schema persists
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    session = Session()
    try:
        yield session
    finally:
        session.close()
