"""User — analyst account with RBAC."""

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(512), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(
        String(64), nullable=False, default="analyst",
        doc="admin | lead_analyst | analyst | viewer",
    )
    permissions: Mapped[list | None] = mapped_column(ARRAY(String(128)), nullable=True)
    preferences: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
