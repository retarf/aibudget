"""SQLAlchemy engine, session factory, and the per-request session dependency."""
import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Connection URL comes from the environment (set via .env / docker-compose).
# The fallback keeps imports working in contexts where it is unset (e.g. tests,
# which override the session dependency anyway).
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://aibudget:change-me@db:5432/aibudget",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a session that is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
