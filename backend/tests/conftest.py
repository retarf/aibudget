"""Shared test fixtures.

Each test gets an isolated in-memory SQLite database and a TestClient whose
`get_db` dependency is overridden to use it.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.models  # noqa: F401  (registers models on Base.metadata)
from backend.database import Base, get_db
from backend.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # one shared connection -> the schema persists
    )
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # No `with` block: TestClient run without the context manager skips the
    # app lifespan, so the real (PostgreSQL) engine is never touched.
    yield TestClient(app)
    app.dependency_overrides.clear()
