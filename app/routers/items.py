from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from ..databases.models.model_item import FavoriteItem, ItemsLike
from ..databases.postgres_orm import get_session
from ..databases.repositories_orm.item import save_image, add_tags, add_items_tags, add_item_db, add_favorite, \
    delete_relation, add_like_db
from ..databases.repositories_sql.items import get_similar_items_db, get_like_items_db, get_tags_from_like, \
    get_favorite_items, get_my_items, get_info_item
from ..schemas.schema_items import HomeDataSchema, ItemSimilarDataSchema, ItemDataSchema, HomeRequest, ItemRequest, \
    ItemInformation
from ..databases.repositories_sql.tags import get_tags_for_item, get_tags
from ..utils import get_user_id

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/get_main", response_model=HomeDataSchema)
async def get_main_items(request: HomeRequest):
    user_id = await get_user_id(request.username)

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
    user_id: int = await get_user_id(data.username)

    limit = 20

    rows = await get_similar_items_db(data.tags, user_id, limit + 1, data.last_id)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemDataSchema(**row) for row in rows]

    return HomeDataSchema(items=items, has_next=has_next)


@router.get("/get_information", response_model=ItemInformation)
async def get_tags_item(id_item: int):
    tags = await get_tags_for_item(id_item)
    info = await get_info_item(id_item)

    return ItemInformation(tags=tags, icon_author=info["path_preview"], author=info["username"], name=info["name"],
                           count_like=info["likes_count"], count_comment=info["comment_count"])


@router.post("/add_item", status_code=201)
async def add_item(
        username: str = Form(...),
        name_item: str = Form(...),
        tags: str = Form(...),
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_session)
):
    tags_list = ["#" + tag for tag in tags.split('#') if tag]

    user_id: int = await get_user_id(username)

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


@router.post("/get_favorite", response_model=HomeDataSchema)
async def get_favorite(request: HomeRequest):
    user_id = await get_user_id(request.username)

    limit = 20

    rows = await get_favorite_items(user_id, request.last_id, limit)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemDataSchema(**row) for row in rows]

    return HomeDataSchema(items=items, has_next=has_next)


@router.post("/get_my_image", response_model=HomeDataSchema)
async def get_my_image(request: HomeRequest):
    user_id = await get_user_id(request.username)

    limit = 20

    rows = await get_my_items(user_id, request.last_id, limit)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemDataSchema(**row) for row in rows]

    return HomeDataSchema(items=items, has_next=has_next)


@router.post("/save_item", status_code=201)
async def save_item(request: ItemRequest, session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(request.username)

    if not await add_favorite(session, user_id, request.id):
        raise HTTPException(status_code=500, detail="Item not added in favorite")

    return Response(status_code=201)


@router.post("/delete_favorite_item", status_code=204)
async def delete_favorite_item(request: ItemRequest, session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(request.username)

    if not await delete_relation(session, FavoriteItem, user_id, request.id):
        raise HTTPException(status_code=500, detail="Item not deleted")

    return Response(status_code=204)


@router.post("/add_like", status_code=201)
async def add_like(request: ItemRequest, session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(request.username)

    if not await add_like_db(session, user_id, request.id):
        raise HTTPException(status_code=500, detail="Item not added in likes")

    return Response(status_code=201)


@router.post("/delete_like", status_code=204)
async def delete_like(request: ItemRequest, session: AsyncSession = Depends(get_session)):
    user_id = await get_user_id(request.username)

    if not await delete_relation(session, ItemsLike, user_id, request.id):
        raise HTTPException(status_code=500, detail="Item not deleted")

    return Response(status_code=204)
