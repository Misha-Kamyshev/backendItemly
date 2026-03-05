from app.databases.postgres_asyncpg import asyncpg_db


async def get_similar_items_db(
        tags: list[str],
        user_id: int,
        limit: int,
        last_id: int | None
) -> list[dict]:
    query = """
            SELECT items.id,
                   items.image_url
            FROM items
                     LEFT JOIN items_like
                               ON items.id = items_like.item_id
                                   AND items_like.user_id = $2
            WHERE items_like.user_id IS NULL
              AND ($3::bigint IS NULL OR items.id < $3)
            ORDER BY CASE
                         WHEN EXISTS (SELECT 1
                                      FROM items_tags it
                                               JOIN tags t ON it.tags_id = t.id
                                      WHERE it.item_id = items.id
                                        AND t.name = ANY ($1::text[]))
                             THEN 0
                         ELSE 1
                         END,
                     items.id DESC
            LIMIT $4
            """

    rows = await asyncpg_db.fetch(query, tags, user_id, last_id, limit)
    return [dict(row) for row in rows]


async def get_like_items_db(user_id: int) -> list[int]:
    query = """
            SELECT item_id
            FROM items_like
            WHERE user_id = $1
            ORDER BY items_like.item_id DESC
            LIMIT 50
            """

    rows = await asyncpg_db.fetch(query, user_id)
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


async def get_favorite_items(user_id: int, last_id: int | None, limit: int) -> list[dict]:
    query = """
            SELECT i.id,
                   i.image_url
            FROM favorite_items f
                     JOIN items i ON i.id = f.item_id
            WHERE f.user_id = $1
              AND ($2::bigint IS NULL OR i.id < $2)
            ORDER BY i.id DESC
            LIMIT $3
            """

    rows = await asyncpg_db.fetch(query, user_id, last_id, limit)
    return [dict(row) for row in rows]


async def get_my_items(user_id: int, last_id: int | None, limit: int) -> list[dict]:
    query = """
            SELECT i.id,
                   i.image_url
            FROM items i
            WHERE i.user_id = $1
              AND ($2::bigint IS NULL OR i.id < $2)
            ORDER BY i.id DESC
            LIMIT $3
            """

    rows = await asyncpg_db.fetch(query, user_id, last_id, limit)
    return [dict(row) for row in rows]


async def get_info_item(id_item: int):
    query = """
            SELECT u.username,
                   u.path_preview,
                   i.name,
                   COUNT(il.user_id)          AS likes_count,
                   0                          AS comment_count,

                   EXISTS(SELECT 1
                          FROM favorite_items
                          WHERE item_id = i.id
                            AND user_id = $2) AS save_item,

                   EXISTS(SELECT 1
                          FROM items_like
                          WHERE item_id = i.id
                            AND user_id = $2) AS like_item

            FROM items i
                     JOIN users u ON i.user_id = u.id
                     LEFT JOIN items_like il ON i.id = il.item_id

            WHERE i.id = $1

            GROUP BY i.id, u.username, u.path_preview, i.name
            """

    row = await asyncpg_db.fetch_row(query, id_item)
    return dict(row) if row else None
