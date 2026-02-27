from typing import List
from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..databases.postgres_orm import get_session
from ..databases.repositories_orm.item import save_image, add_tags, add_items_tags, add_item_db
from ..databases.repositories_sql.items import get_similar_items_db, get_like_items_db, get_tags_from_like, \
    get_bonus_items_db
from ..databases.repositories_sql.user import get_user
from ..schemas.schema_items import HomeDataSchema, ItemSimilarDataSchema
from ..databases.repositories_sql.tags import get_tags_for_item, get_tags

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


@router.post("/add_item", status_code=201)
async def add_item(
    username: str = Form(...),
    name_item: str = Form(...),
    tags: list[str] = Form(...),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    user = await get_user(username)
    user_id: int = user["id"]

    path_image = await save_image(image, user_id)

    item = await add_item_db(session, user_id, path_image, name_item)
    if item is None:
        raise HTTPException(status_code=500, detail="Item not created")
    item_id = item.id

    if not await add_tags(session, tags):
        raise HTTPException(status_code=500, detail="Tags not added in tags")
    id_tags = await get_tags(tags)

    if not await add_items_tags(session, item_id, id_tags):
        raise HTTPException(status_code=500, detail="Tags not added in items_tags")

    return {
        "item_id": item_id,
        "tags": tags,
        "image_url": path_image
    }
