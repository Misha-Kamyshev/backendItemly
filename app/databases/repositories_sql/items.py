from typing import Any

from app.databases.postgres_asyncpg import asyncpg_db


async def get_similar_items_db(tags: list[str], username: str) -> list[dict[str, Any]]:
    query = """
            SELECT DISTINCT items.id,
                            items.image_url
            FROM items
                     JOIN items_tags ON items.id = items_tags.item_id
                     JOIN tags ON items_tags.tags_id = tags.id
                     LEFT JOIN items_like
                               ON items.id = items_like.item_id
                                   AND items_like.user_id = (SELECT id FROM users WHERE username = $2)
            WHERE tags.name = ANY ($1::text[])
              AND items_like.user_id IS NULL
            ORDER BY items.id
            """

    rows = await asyncpg_db.fetch(query, tags, username)
    return [dict(row) for row in rows]


async def get_like_items_db(username: str) -> list[int]:
    query = """
            SELECT items_like.item_id
            FROM items_like
                     join users u on u.id = items_like.user_id
            where u.username = $1
            ORDER BY items_like.item_id DESC
            LIMIT 50
            """

    rows = await asyncpg_db.fetch(query, username)
    return [row["item_id"] for row in rows]


async def get_tags_from_like(items: list[int]) -> list[str]:
    query = """
            SELECT items_tags.item_id,
                   array_agg(tags.name) as name
            FROM items_tags
                     JOIN tags ON items_tags.tags_id = tags.id
            WHERE items_tags.item_id = ANY ($1::int[])
            GROUP BY items_tags.item_id
            """

    rows = await asyncpg_db.fetch(query, items)
    result = []
    for row in rows:
        result.append(row["name"])

    return result


async def get_bonus_items_db() -> list[dict[str, Any]]:
    query = """
            SELECT id, image_url
            FROM items
            ORDER BY RANDOM()
            LIMIT 20
            """

    rows = await asyncpg_db.fetch(query)
    return [dict(row) for row in rows]
