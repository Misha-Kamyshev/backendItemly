from typing import List
from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from ..databases.postgres_orm import get_session
from ..databases.repositories_orm.item import save_image, add_tags, add_items_tags, add_item_db
from ..databases.repositories_sql.items import get_similar_items_db, get_like_items_db, get_tags_from_like
from ..databases.repositories_sql.user import get_user
from ..schemas.schema_items import HomeDataSchema, ItemSimilarDataSchema, ItemDataSchema, HomeRequest
from ..databases.repositories_sql.tags import get_tags_for_item, get_tags

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/get_main", response_model=HomeDataSchema)
async def get_main_items(request: HomeRequest):
    user = await get_user(request.username)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    user_id: int = user["id"]

    like_items_user = await get_like_items_db(user_id)
    tags_user = await get_tags_from_like(like_items_user)

    limit = 20

    rows = await get_similar_items_db(tags_user, user_id, limit + 1, request.last_id)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemDataSchema(**row) for row in rows]

    return HomeDataSchema(items=items, has_next=has_next)


@router.post("/get_similar_images", response_model=HomeDataSchema)
async def get_similar_items(data: ItemSimilarDataSchema):
    user = await get_user(data.username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user_id: int = user["id"]

    limit = 20

    rows = await get_similar_items_db(data.tags, user_id, limit + 1, data.last_id)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemDataSchema(**row) for row in rows]

    return HomeDataSchema(items=items, has_next=has_next)


@router.get("/get_tags", response_model=List[str])
async def get_tags_item(id_item: int):
    return await get_tags_for_item(id_item)


@router.post("/add_item", status_code=201)
async def add_item(
        username: str = Form(...),
        name_item: str = Form(...),
        tags: str = Form(...),
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_session)
):
    tags_list = ["#" + tag for tag in tags.split('#') if tag]

    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user_id: int = user["id"]

    path_image = await save_image(image, user_id)

    item = await add_item_db(session, user_id, path_image, name_item)
    if item is None:
        raise HTTPException(status_code=500, detail="Item not created")
    item_id = item.id

    if not await add_tags(session, tags_list):
        raise HTTPException(status_code=500, detail="Tags not added in tags")
    id_tags = await get_tags(tags_list)

    if not await add_items_tags(session, item_id, id_tags):
        raise HTTPException(status_code=500, detail="Tags not added in items_tags")

    return Response(status_code=201)