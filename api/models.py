from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, registry, relationship
from sqlalchemy import func, ForeignKey
from datetime import datetime, date
from typing import List

table_registry = registry()


@table_registry.mapped_as_dataclass
class Users:
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column(index=True)

    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    books: Mapped[List["Wishlist"]] = relationship(
        back_populates="user",
        init=False,
        default_factory=list,
        lazy="noload",
    )


@table_registry.mapped_as_dataclass
class Wishlist:
    __tablename__ = "Wishlist"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    author: Mapped[str]
    publisher: Mapped[str]
    published_date: Mapped[date]
    description: Mapped[str]
    page_count: Mapped[int]
    buylink: Mapped[str]
    language: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    user: Mapped["Users"] = relationship(back_populates="books", init=False)
