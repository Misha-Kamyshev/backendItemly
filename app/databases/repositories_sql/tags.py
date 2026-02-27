from typing import List

from app.databases.postgres_asyncpg import asyncpg_db


async def get_tags_for_item(item_id: int) -> List[str]:
    query = """
            SELECT tags.name
            FROM items_tags
                     join tags ON items_tags.tags_id = tags.id
            where item_id = $1
            """

    rows = await asyncpg_db.fetch(query, item_id)
    return [row["name"] for row in rows]

async def get_tags(names: list[str]) -> list[int]:
    query = """
        SELECT id
        FROM tags
            WHERE name = ANY ($1::text[])
    """
    rows = await asyncpg_db.fetch(query, names)
    return [row["id"] for row in rows]
