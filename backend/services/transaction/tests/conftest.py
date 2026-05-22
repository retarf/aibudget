"""Test fixtures for transaction-service — isolated in-memory SQLite per test."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.services.transaction import models  # noqa: F401  (registers ORM models)
from backend.services.transaction.database import Base


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
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
