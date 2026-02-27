from typing import List
from fastapi import APIRouter

from ..databases.repositories_sql.items import get_similar_items_db, get_like_items_db, get_tags_from_like, \
    get_bonus_items_db
from ..schemas.schema_items import HomeDataSchema, ItemSimilarDataSchema
from ..databases.repositories_sql.tags import get_tags_for_item

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/get_main", response_model=list[HomeDataSchema])
async def get_main_items(username: str):
    like_items_user = await get_like_items_db(username)
    tags_user = await get_tags_from_like(like_items_user)
    result = await get_similar_items_db(tags_user, username)
    if len(result) < 10:
        bonus_result: list = await get_bonus_items_db()
        result.extend(bonus_result)

    seen = set()
    unique_result = []
    for item in result:
        if item['id'] not in seen:
            seen.add(item['id'])
            unique_result.append(item)

    return unique_result


@router.post("/get_similar_images", response_model=list[HomeDataSchema])
async def get_similar_items(data: ItemSimilarDataSchema):
    return await get_similar_items_db(data.tags, data.username)


@router.get("/get_tags", response_model=List[str])
async def get_tags_item(id_item: int):
    return await get_tags_for_item(id_item)
