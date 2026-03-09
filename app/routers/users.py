from typing import Any

from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgres_orm import get_session
from app.databases.repositories_orm.user import create_user, create_path_preview, save_image_preview
from app.databases.repositories_sql.user import get_user, get_image_user_db
from app.security.crypt import hash_password, verify_password
from app.security.jwt import create_access_token, create_refresh_token
from app.schemas.schema_user import CreateUserSchema, PushDataUserSchema, LoginUserSchema, PushPreviewImageUserSchema
from app.utils import get_user_id

router = APIRouter(prefix="/user", tags=["Catalog"])


@router.post("/signup", response_model=PushDataUserSchema, status_code=201)
async def sign_up(data: CreateUserSchema, session: AsyncSession = Depends(get_session)):
    try:
        user = await create_user(session, data.username, data.email, hash_password(data.password))
        access_token = create_access_token(user.id, user.username)
        refresh_token = create_refresh_token(user.id, user.username)
        return PushDataUserSchema(
            username=user.username,
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Логин или почта уже заняты")


@router.post("/signin", response_model=PushDataUserSchema)
async def sign_in(data: LoginUserSchema):
    result_db: dict[str, Any] | None

    result_db = await get_user(data.login)

    if result_db is None:
        raise HTTPException(status_code=400, detail="Такой пользователь не зарегистрирован")

    elif not verify_password(data.password, result_db["password"]):
        raise HTTPException(status_code=400, detail="Не правильный пароль")

    username: str = result_db["username"]
    email: str = result_db["email"]
    access_token = create_access_token(result_db['id'], username)
    refresh_token = create_refresh_token(result_db['id'], username)

    return PushDataUserSchema(
        username=username,
        email=email,
        access_token=access_token,
        refresh_token=refresh_token
    )



@router.post("/change_preview", status_code=201)
async def change_preview(
        username: str = Form(...),
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_session)
):
    user_id = await get_user_id(username)

    path_preview = await save_image_preview(image, user_id)

    if not create_path_preview(session, user_id, path_preview):
        raise HTTPException(status_code=500, detail="Error in server")

    return Response(status_code=201)


@router.post("/get_image_user", response_model=PushPreviewImageUserSchema)
async def get_image_user(username: str):
    user_id = await get_user_id(username)

    return await get_image_user_db(user_id)
