from typing import Any

from app.databases.postgres_asyncpg import asyncpg_db


async def get_user(login: str) -> dict[str, Any] | None:
    query = """
        SELECT id, username, email, password
        FROM users
        WHERE username = $1 OR email = $1
        LIMIT 1
    """
    row = await asyncpg_db.fetch_row(query, login)
    return dict(row) if row else None

async def get_image_user_db(user_id: int) -> dict[str, Any] | None:
    query = """
    SELECT path_preview
    FROM users 
        WHERE id = $1
    """
    row = await asyncpg_db.fetch_row(query, user_id)
    return dict(row) if row else None
