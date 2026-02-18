from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgres_orm import get_session
from app.databases.repositories_orm.user import create_user
from app.databases.repositories_sql.user import get_user
from app.security.crypt import hash_password, verify_password
from app.security.jwt import create_access_token, create_refresh_token
from app.schemas.schema_user import CreateUserSchema, PushDataUserSchema, LoginUserSchema

router = APIRouter(prefix="/user", tags=["Catalog"])


@router.post("/signup", response_model=PushDataUserSchema, status_code=201)
async def sign_up(data: CreateUserSchema, session: AsyncSession = Depends(get_session)):
    try:
        user = await create_user(session, data.username, data.email, hash_password(data.password))
        access_token = create_access_token(user.id, user.username)
        refresh_token = create_refresh_token(user.id, user.username)
        return PushDataUserSchema(
            username=user.username,
            access_token=access_token,
            refresh_token=refresh_token
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Логин или почта уже заняты")


@router.post("/login", response_model=PushDataUserSchema)
async def sign_in(data: LoginUserSchema):
    result_db: dict[str, Any] | None

    login_value = data.username or data.email
    result_db = await get_user(login_value)

    if result_db is None:
        raise HTTPException(status_code=400, detail="Такой пользователь не зарегистрирован")

    elif not verify_password(data.password, result_db["password"]):
        raise HTTPException(status_code=400, detail="Не правильный пароль")

    username: str = result_db["username"]
    access_token = create_access_token(result_db['id'], username)
    refresh_token = create_refresh_token(result_db['id'], username)

    return PushDataUserSchema(
        username=username,
        access_token=access_token,
        refresh_token=refresh_token
    )
