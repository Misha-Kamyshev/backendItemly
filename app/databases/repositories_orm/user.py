import os, aiofiles

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.model_user import User


async def create_user(session: AsyncSession, username: str, email: str, password: str) -> User:
    user = User(username=username, email=email, password=password)
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        return user

    except IntegrityError:
        await session.rollback()
        raise ValueError('Username или email заняты')


async def create_path_preview(session: AsyncSession, user_id: int, preview_path: str) -> bool:
    user = await session.get(User, user_id)
    if user is None:
        return False

    if user.path_preview:
        return True

    user.path_preview = preview_path
    try:
        await session.commit()
        return True
    except IntegrityError:
        await session.rollback()
        raise ValueError("Error update path")


async def save_image_preview(image: UploadFile, user_id: int) -> str:
    ext = image.filename.split(".")[-1]

    folder_path = f"static/{user_id}"
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"preview_image.{ext}")

    async with aiofiles.open(file_path, "wb") as out_file:
        content = await image.read()
        await out_file.write(content)

    return file_path
