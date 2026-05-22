"""ORM models for category-service."""
from sqlalchemy import Enum, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.schemas import CategoryKind

from .database import Base


class Category(Base):
    """A label used to classify incomes or expenses."""

    __tablename__ = "categories"
    # A category name is unique within its kind, but the same name may exist
    # for both an income and an expense category.
    __table_args__ = (
        UniqueConstraint("name", "kind", name="uq_category_name_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    kind: Mapped[CategoryKind] = mapped_column(
        Enum(CategoryKind), nullable=False
    )
