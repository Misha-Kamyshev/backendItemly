from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from .base import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_url: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)


class ItemsLike(Base):
    __tablename__ = "items_likes"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), primary_key=True)


class ItemsTags(Base):
    __tablename__ = "items_tags"

    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), primary_key=True)
    tags_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)


class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class FavoriteItem(Base):
    __tablename__ = "favorite_items"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), primary_key=True)
