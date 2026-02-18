from typing import Optional
from asyncpg import create_pool, Pool


class AsyncPG:
    def __init__(self):
        self.pool: Optional[Pool] = None

    async def connect(self, dsn: str) -> None:
        self.pool = await create_pool(
            dsn=dsn,
            min_size=1,
            max_size=10,
        )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetch_row(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)


asyncpg_db = AsyncPG()
