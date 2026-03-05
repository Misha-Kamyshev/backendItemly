import os
import uuid
import aiofiles

from typing import Type
from fastapi import UploadFile
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.models.model_item import Item, ItemsTags, Tags, FavoriteItem, ItemsLike
from ..models.base import Base


async def add_item_db(session: AsyncSession, user_id: int, image_url: str, name: str) -> Item | None:
    item = Item(image_url=image_url, user_id=user_id, name=name)
    session.add(item)
    try:
        await session.commit()
        await session.refresh(item)
        return item
    except IntegrityError:
        await session.rollback()
        return None


async def add_items_tags(session: AsyncSession, item_id: int, tags: list[int]) -> bool:
    stmt = insert(ItemsTags).values(
        [{"item_id": item_id, "tags_id": tag_id} for tag_id in tags]
    ).on_conflict_do_nothing(index_elements=["item_id", "tags_id"])

    try:
        await session.execute(stmt)
        await session.commit()
        return True
    except IntegrityError:
        await session.rollback()
        return False


async def add_tags(session: AsyncSession, names: list[str]) -> bool:
    try:
        for tag_name in names:
            stmt = insert(Tags).values(name=tag_name).on_conflict_do_nothing(index_elements=["name"])
            await session.execute(stmt)
        await session.commit()
        return True
    except IntegrityError:
        await session.rollback()
        return False


async def add_favorite(session: AsyncSession, user_id: int, item_id: int) -> bool:
    favorite_item = FavoriteItem(user_id=user_id, item_id=item_id)
    session.add(favorite_item)

    try:
        await session.commit()
        return True
    except IntegrityError:
        await session.rollback()
        return False


async def delete_relation(
        session: AsyncSession,
        model: Type[Base],
        user_id: int,
        item_id: int
) -> bool:
    obj = await session.get(model, (user_id, item_id))

    if not obj:
        return True

    try:
        await session.delete(obj)
        await session.commit()
        return True
    except SQLAlchemyError:
        await session.rollback()
        return False


async def add_like_db(session: AsyncSession, user_id: int, item_id: int) -> bool:
    item_like = ItemsLike(user_id=user_id, item_id=item_id)
    session.add(item_like)

    try:
        await session.commit()
        return True
    except IntegrityError:
        await session.rollback()
        return False


async def save_image(image: UploadFile, user_id: int) -> str:
    uid = str(uuid.uuid4())
    ext = image.filename.split(".")[-1]

    folder_path = f"static/{user_id}"
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{uid}.{ext}")

    async with aiofiles.open(file_path, "wb") as out_file:
        content = await image.read()
        await out_file.write(content)

    return file_path
