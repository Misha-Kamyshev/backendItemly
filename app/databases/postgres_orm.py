from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

engine: Optional[object] = None
AsyncSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def init_engine(dsn: str) -> None:
    """
    Инициализирует async engine и sessionmaker для SQLAlchemy
    """
    global engine, AsyncSessionLocal

    engine = create_async_engine(
        dsn,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Генератор сессий для FastAPI.
    Используется через Depends().
    """
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database engine is not initialized. "
            "Call init_engine(dsn) before using get_session()"
        )

    async with AsyncSessionLocal() as session:
        yield session
