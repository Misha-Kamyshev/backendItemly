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
