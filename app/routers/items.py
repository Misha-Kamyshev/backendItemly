from fastapi import APIRouter, HTTPException, File, Form, UploadFile, Security, Query
from fastapi.params import Depends
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from ..databases.models.model_item import FavoriteItem, ItemsLike
from ..databases.postgres_orm import get_session
from ..databases.repositories_orm.item import save_image, add_tags, add_items_tags, add_item_db, add_favorite, \
    delete_relation, add_like_db, delete_item_db
from ..databases.repositories_sql.items import get_similar_items_db, get_like_items_db, get_tags_from_like, \
    get_favorite_items, get_my_items, get_info_item, get_like_db, get_items_author_db, search_items_db
from ..schemas.schema_items import ItemsDataResponse, ItemSimilarRequest, ItemData, ItemInformationResponse, SearchRequest
from ..databases.repositories_sql.tags import get_tags_for_item, get_tags
from ..static import access_security

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/get_main", response_model=ItemsDataResponse)
async def get_main_items(
        last_id: int | None = Query(None, description="last_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
):
    user_id: int = credentials.subject["id"]

    like_items_user = await get_like_items_db(user_id)
    tags_user = await get_tags_from_like(like_items_user)

    limit = 20

    rows = await get_similar_items_db(tags_user, user_id, limit + 1, last_id)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemData(**row) for row in rows]

    return ItemsDataResponse(items=items, has_next=has_next)


@router.post("/get_similar_images", response_model=ItemsDataResponse)
async def get_similar_items(
        data: ItemSimilarRequest,
        credentials: JwtAuthorizationCredentials = Security(access_security)
):
    user_id: int = credentials.subject["id"]

    limit = 20

    rows = await get_similar_items_db(data.tags, user_id, limit + 1, data.last_id)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemData(**row) for row in rows]

    return ItemsDataResponse(items=items, has_next=has_next)


@router.get("/get_information", response_model=ItemInformationResponse)
async def get_information_item(
        id_item: int = Query(None, description="item_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security)
):
    user_id: int = credentials.subject["id"]

    tags = await get_tags_for_item(id_item)
    info = await get_info_item(id_item, user_id)

    return ItemInformationResponse(tags=tags, icon_author=info["path_preview"], author=info["username"], name=info["name"],
                                   count_like=info["likes_count"], save_item=info["save_item"], like_item=info["like_item"])


@router.post("/add_item", status_code=201)
async def add_item(
        name_item: str = Form(...),
        tags: str = Form(...),
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_session),
        credentials: JwtAuthorizationCredentials = Security(access_security)
):
    tags_list = tags.split(';')

    user_id: int = credentials.subject["id"]

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


@router.post("/get_favorite", response_model=ItemsDataResponse)
async def get_favorite(
        last_id: int | None = Query(None, description="last_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
):
    user_id: int = credentials.subject["id"]

    limit = 20

    rows = await get_favorite_items(user_id, last_id, limit)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemData(**row) for row in rows]

    return ItemsDataResponse(items=items, has_next=has_next)


@router.post("/get_my_image", response_model=ItemsDataResponse)
async def get_my_image(
        last_id: int | None = Query(None, description="last_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
):
    user_id: int = credentials.subject["id"]

    limit = 20

    rows = await get_my_items(user_id, last_id, limit)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemData(**row) for row in rows]

    return ItemsDataResponse(items=items, has_next=has_next)


@router.post("/save_item", status_code=201)
async def save_item(
        item_id: int = Query(None, description="item_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
        session: AsyncSession = Depends(get_session)
):
    user_id: int = credentials.subject["id"]

    if not await add_favorite(session, user_id, item_id):
        raise HTTPException(status_code=500, detail="Item not added in favorite")

    return Response(status_code=201)


@router.post("/delete_favorite_item", status_code=204)
async def delete_favorite_item(
        item_id: int = Query(None, description="item_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
        session: AsyncSession = Depends(get_session)
):
    user_id: int = credentials.subject["id"]

    if not await delete_relation(session, FavoriteItem, user_id, item_id):
        raise HTTPException(status_code=500, detail="Item not deleted")

    return Response(status_code=204)


@router.post("/add_like", status_code=201)
async def add_like(
        item_id: int = Query(None, description="item_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
        session: AsyncSession = Depends(get_session)
):
    user_id: int = credentials.subject["id"]

    if not await add_like_db(session, user_id, item_id):
        raise HTTPException(status_code=500, detail="Item not added in likes")

    return Response(status_code=201)


@router.post("/delete_like", status_code=204)
async def delete_like(
        item_id: int = Query(None, description="item_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
        session: AsyncSession = Depends(get_session)
):
    user_id: int = credentials.subject["id"]

    if not await delete_relation(session, ItemsLike, user_id, item_id):
        raise HTTPException(status_code=500, detail="Item not deleted")

    return Response(status_code=204)


@router.post("/get_like", response_model=ItemsDataResponse)
async def get_like(
        last_id: int | None = Query(None, description="last_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
):
    user_id: int = credentials.subject["id"]
    limit = 20

    rows = await get_like_db(user_id, last_id, limit)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemData(**row) for row in rows]

    return ItemsDataResponse(items=items, has_next=has_next)


@router.post("/get_items_author", response_model=ItemsDataResponse)
async def get_items_author(
        last_id: int | None = Query(None, description="last_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
):
    user_id: int = credentials.subject["id"]

    limit = 20

    rows = await get_items_author_db(user_id, last_id, limit)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemData(**row) for row in rows]

    return ItemsDataResponse(items=items, has_next=has_next)


@router.post("/delete_item", status_code=204)
async def delete_item(
        item_id: int = Query(None, description="item_id"),
        credentials: JwtAuthorizationCredentials = Security(access_security),
        session: AsyncSession = Depends(get_session)
):
    user_id: int = credentials.subject["id"]

    if not await delete_item_db(session, user_id, item_id):
        raise HTTPException(status_code=500, detail="Item not deleted")

    return Response(status_code=204)


@router.post("/search_items", response_model=ItemsDataResponse)
async def search_items(
        request: SearchRequest,
        _: JwtAuthorizationCredentials = Security(access_security),
):
    limit = 20

    rows = await search_items_db(request.query, request.last_id, limit)

    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    items = [ItemData(**row) for row in rows]

    return ItemsDataResponse(items=items, has_next=has_next)
