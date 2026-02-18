from typing import Any

from app.databases.postgres_asyncpg import asyncpg_db


async def get_user(login: str) -> dict[str, Any] | None:
    query = """
        SELECT id, username, password
        FROM users
        WHERE username = $1 OR email = $1
        LIMIT 1
    """
    row = await asyncpg_db.fetch_row(query, login)
    return dict(row) if row else None
